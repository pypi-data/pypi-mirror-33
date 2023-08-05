from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import tensorflow as tf
import numpy as np

from tefla.core.decoder import BasicDecoder, AttentionDecoder, AttentionLayerDot, BeamSearchDecoder
from tefla.core import beam_search
from tefla.utils import seq2seq_utils as decode_helper


class DecoderTests(object):
  """
    A collection of decoder tests. This class should be inherited together with
    `tf.test.TestCase`.
    """

  def __init__(self):
    self.batch_size = 4
    self.sequence_length = 16
    self.input_depth = 10
    self.vocab_size = 100
    self.max_decode_length = 20

  def create_decoder(self, helper, mode, reuse):
    """Creates the decoder module.

        This must be implemented by child classes and instantiate the appropriate
        decoder to be tested.
        """
    raise NotImplementedError

  def test_with_fixed_inputs(self):
    inputs = tf.random_normal([self.batch_size, self.sequence_length, self.input_depth])
    seq_length = tf.ones(self.batch_size, dtype=tf.int32) * self.sequence_length

    helper = decode_helper.TrainingHelper(inputs=inputs, sequence_length=seq_length)
    decoder_fn = self.create_decoder(
        helper=helper, mode=tf.estimator.ModeKeys.TRAIN, reuse=None)
    initial_state = decoder_fn.cell.zero_state(self.batch_size, dtype=tf.float32)
    decoder_output, _ = decoder_fn(initial_state, helper)

    # pylint: disable=E1101
    with self.test_session() as sess:
      sess.run(tf.global_variables_initializer())
      decoder_output_ = sess.run(decoder_output)

    self.assertAllEqual(decoder_output_.logits.shape,
                        [self.sequence_length, self.batch_size, self.vocab_size])
    self.assertAllEqual(decoder_output_.predicted_ids.shape,
                        [self.sequence_length, self.batch_size])

    return decoder_output_

  def test_gradients(self):
    inputs = tf.random_normal([self.batch_size, self.sequence_length, self.input_depth])
    seq_length = tf.ones(self.batch_size, dtype=tf.int32) * self.sequence_length
    labels = np.random.randint(0, self.vocab_size, [self.batch_size, self.sequence_length])

    helper = decode_helper.TrainingHelper(inputs=inputs, sequence_length=seq_length)
    decoder_fn = self.create_decoder(
        helper=helper, mode=tf.estimator.ModeKeys.TRAIN, reuse=None)
    initial_state = decoder_fn.cell.zero_state(self.batch_size, dtype=tf.float32)
    decoder_output, _ = decoder_fn(initial_state, helper)

    losses = tf.nn.sparse_softmax_cross_entropy_with_logits(
        logits=tf.transpose(decoder_output.logits, [1, 0, 2]), labels=labels)
    optimizer = tf.train.AdamOptimizer(learning_rate=0.001)
    grads_and_vars = optimizer.compute_gradients(tf.reduce_mean(losses))

    # pylint: disable=E1101
    with self.test_session() as sess:
      sess.run(tf.global_variables_initializer())
      grads_and_vars_ = sess.run(grads_and_vars)

    for grad, _ in grads_and_vars_:
      self.assertFalse(np.isnan(grad).any())

    return grads_and_vars_

  def test_with_dynamic_inputs(self):
    embeddings = tf.get_variable("W_embed", [self.vocab_size, self.input_depth])

    helper = decode_helper.GreedyEmbeddingHelper(
        embedding=embeddings, start_tokens=[0] * self.batch_size, end_token=-1)
    decoder_fn = self.create_decoder(
        helper=helper, mode=tf.estimator.ModeKeys.PREDICT, reuse=None)
    initial_state = decoder_fn.cell.zero_state(self.batch_size, dtype=tf.float32)
    decoder_output, _ = decoder_fn(initial_state, helper)

    # pylint: disable=E1101
    with self.test_session() as sess:
      sess.run(tf.global_variables_initializer())
      decoder_output_ = sess.run(decoder_output)

    self.assertAllEqual(decoder_output_.logits.shape,
                        [self.max_decode_length, self.batch_size, self.vocab_size])
    self.assertAllEqual(decoder_output_.predicted_ids.shape,
                        [self.max_decode_length, self.batch_size])

  def test_with_beam_search(self):
    self.batch_size = 1

    # Batch size for beam search must be 1.
    config = beam_search.BeamSearchConfig(
        beam_width=10,
        vocab_size=self.vocab_size,
        eos_token=self.vocab_size - 2,
        length_penalty_weight=0.6,
        choose_successors_fn=beam_search.choose_top_k)

    embeddings = tf.get_variable("W_embed", [self.vocab_size, self.input_depth])

    helper = decode_helper.GreedyEmbeddingHelper(
        embedding=embeddings, start_tokens=[0] * config.beam_width, end_token=-1)
    decoder_fn = self.create_decoder(
        helper=helper, mode=tf.estimator.ModeKeys.PREDICT, reuse=None)
    decoder_fn = BeamSearchDecoder(decoder=decoder_fn, config=config)

    initial_state = decoder_fn.cell.zero_state(self.batch_size, dtype=tf.float32)
    decoder_output, _ = decoder_fn(initial_state, helper)

    # pylint: disable=E1101
    with self.test_session() as sess:
      sess.run(tf.global_variables_initializer())
      decoder_output_ = sess.run(decoder_output)

    self.assertAllEqual(decoder_output_.predicted_ids.shape,
                        [self.max_decode_length, 1, config.beam_width])
    self.assertAllEqual(decoder_output_.beam_search_output.beam_parent_ids.shape,
                        [self.max_decode_length, 1, config.beam_width])
    self.assertAllEqual(decoder_output_.beam_search_output.scores.shape,
                        [self.max_decode_length, 1, config.beam_width])
    self.assertAllEqual(decoder_output_.beam_search_output.original_outputs.predicted_ids.shape,
                        [self.max_decode_length, 1, config.beam_width])
    self.assertAllEqual(decoder_output_.beam_search_output.original_outputs.logits.shape,
                        [self.max_decode_length, 1, config.beam_width, self.vocab_size])

    return decoder_output


class BasicDecoderTest(tf.test.TestCase, DecoderTests):
  """Tests the `BasicDecoder` class.
    """

  def setUp(self):
    tf.test.TestCase.setUp(self)
    tf.logging.set_verbosity(tf.logging.INFO)
    DecoderTests.__init__(self)

  def create_decoder(self, helper, mode, reuse):
    params = BasicDecoder.default_params()
    params["max_decode_length"] = self.max_decode_length
    decoder = BasicDecoder(params=params, mode=mode, reuse=reuse, vocab_size=self.vocab_size)

    return decoder


class AttentionDecoderTest(tf.test.TestCase, DecoderTests):
  """Tests the `AttentionDecoder` class.
    """

  def setUp(self):
    tf.test.TestCase.setUp(self)
    tf.logging.set_verbosity(tf.logging.INFO)
    DecoderTests.__init__(self)
    self.attention_dim = 64
    self.input_seq_len = 10

  def create_decoder(self, helper, mode, reuse):
    attention_fn = AttentionLayerDot(
        params={"num_units": self.attention_dim}, mode=tf.estimator.ModeKeys.TRAIN, reuse=reuse)
    attention_values = tf.convert_to_tensor(
        np.random.randn(self.batch_size, self.input_seq_len, 32), dtype=tf.float32)
    attention_keys = tf.convert_to_tensor(
        np.random.randn(self.batch_size, self.input_seq_len, 32), dtype=tf.float32)
    params = AttentionDecoder.default_params()
    params["max_decode_length"] = self.max_decode_length
    return AttentionDecoder(
        params=params,
        mode=mode,
        reuse=reuse,
        vocab_size=self.vocab_size,
        attention_keys=attention_keys,
        attention_values=attention_values,
        attention_values_length=np.arange(self.batch_size) + 1,
        attention_fn=attention_fn)

  def test_attention_scores(self):
    decoder_output_ = self.test_with_fixed_inputs()
    self.assertAllEqual(decoder_output_.attention_scores.shape,
                        [self.sequence_length, self.batch_size, self.input_seq_len])

    # Make sure the attention scores sum to 1 for each step
    scores_sum = np.sum(decoder_output_.attention_scores, axis=2)
    self.assertNDArrayNear(scores_sum, np.ones([self.sequence_length, self.batch_size]), 0.00001)


if __name__ == "__main__":
  tf.test.main()
