#!/bin/bash

read -r -d '' patg <<HEREDOC1
04000a52616e646f6d53656564.{16}
04000473656564.{16}
04000744617954696d65.{16}
04000a4c617374506c61796564.{16}
HEREDOC1

read -r -d '' pats <<HEREDOC2
s_04000a52616e646f6d53656564_RandomSeed _
s_04000473656564_seed _
s_04000744617954696d65_DayTime _
s_04000a4c617374506c61796564_LastPlayed _
HEREDOC2

read -r -d '' pyc <<HEREDOC3
import sys
print(int.from_bytes(bytes.fromhex(sys.stdin.readline()), signed=True))
HEREDOC3

for f in ${@}; do
  echo ${f}
  buf=$(zcat ${f} | xxd -p -c0 | grep -oEf <(echo "${patg}") | sed -f <(echo "${pats}") | sort -u)
  echo "${buf}"
  echo "${buf}" | grep -i seed | cut -d' ' -f2 | python3 -c "${pyc}"
  echo
done
