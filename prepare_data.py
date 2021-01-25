import os
import argparse
import pickle

import torch
import torch.nn.functional as F


def main():
  parser = argparse.ArgumentParser("Configuration for data preparation")
  parser.add_argument("--librispeech_from_kaldi", default="./librispeech_data/kaldi/dev-clean-hires-norm.blogmel", type=str,
    help="Path to the librispeech log Mel features generated by the Kaldi scripts")
  parser.add_argument("--max_seq_len", default=1600, type=int,
    help="The maximum length (number of frames) of each sequence; sequences will be truncated or padded (with zero vectors) to this length")
  parser.add_argument("--save_dir", default="./librispeech_data/preprocessed/dev-clean", type=str,
    help="Directory to save the preprocessed pytorch tensors")
  config = parser.parse_args()

  os.makedirs(config.save_dir, exist_ok=True)

  id2len = {}
  with open(config.librispeech_from_kaldi, 'r') as f:
    # process the file line by line
    for line in f:
      data = line.strip().split()

      if len(data) == 1:
        if data[0] == '.':  # end of the current utterance
          id2len[utt_id + '.pt'] = min(len(log_mel), config.max_seq_len)
          log_mel = torch.FloatTensor(log_mel)  # convert the 2D list to a pytorch tensor
          log_mel = F.pad(log_mel, (0, 0, 0, config.max_seq_len - log_mel.size(0))) # pad or truncate
          torch.save(log_mel, os.path.join(config.save_dir, utt_id + '.pt'))

        else: # here starts a new utterance
          utt_id = data[0]
          log_mel = []

      else:
        log_mel.append([float(i) for i in data])

  with open(os.path.join(config.save_dir, 'lengths.pkl'), 'wb') as f:
    pickle.dump(id2len, f, protocol=4)


if __name__ == '__main__':
  main()
