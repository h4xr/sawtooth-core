# Copyright 2016 Intel Corporation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ------------------------------------------------------------------------------

import time

from sawtooth_validator.journal.consensus.consensus import \
    BlockPublisherInterface, BlockVerifierInterface


class BlockPublisher(BlockPublisherInterface):
    """Consensus objects provide the following services to the Journal:
    1) Build candidate blocks ( this temporary until the block types are
    combined into a single block type)
    2) Check if it is time to claim the current candidate blocks.
    3) Provide the data a signatures required for a block to be validated by
    other consensus algorithms

    """

    def __init__(self, num_batches_per_block=1):
        self._num_batches = num_batches_per_block
        self._count = 0

    def initialize_block(self, block_header):
        """Do initialization necessary for the consensus to claim a block,
        this may include initiating voting activates, starting proof of work
        hash generation, or create a PoET wait timer.

        Args:
            journal (Journal): the current journal object
            block (TransactionBlock): the block to initialize.
        Returns:
            none
        """
        block_header.consensus = b"Devmode"

    def check_publish_block(self, block):
        """Check if a candidate block is ready to be claimed.

        Args:
            journal (Journal): the current journal object
            block: the block to be checked if it should be claimed
            now: the current time
        Returns:
            Boolean: True if the candidate block should be claimed.
        """
        if self._count >= self._num_batches:
            self._count = 0
            return True
        self._count += 1
        return False

    def finalize_block(self, block_header):
        """Finalize a block to be claimed. Provide any signatures and
        data updates that need to be applied to the block before it is
        signed and broadcast to the network.

        Args:
            journal (Journal): the current journal object
            block: The candidate block that
        Returns:
            None
        """
        pass


class TimedBlockPublisher(BlockPublisherInterface):
    """Provides a timed block claim mechanism based on
    the number of seconds since that validator last claimed
    a block"""

    def __init__(self, wait_time=20):
        self._wait_time = wait_time
        self._last_block_time = time.time()

    def initialize_block(self, block_header):
        block_header.consensus = b"TimedDevmode"

    def check_publish_block(self, block):
        if time.time() - self._last_block_time > self._wait_time:
            self._last_block_time = time.time()
            return True
        return False

    def finalize_block(self, block_header):
        pass


class BlockVerifier(BlockVerifierInterface):
    def verify_block(self, block_state):
        return True

    def compute_block_weight(self, block_state):
        # longest chain wins
        return block_state.block_num
