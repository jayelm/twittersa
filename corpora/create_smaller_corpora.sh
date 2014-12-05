sizes=( 100 250 500 750 1000 2500 5000 7500 10000 15000 20000 25000 250000)
for i in "${sizes[@]}"; do
    shuf -o ./training.1600000.processed.noemoticon.csv.shuffled < ./training.1600000.processed.noemoticon.csv.shuffled
    fout="./training.$i.csv"
    echo "Writing to $fout"
    tail -n "$i" ./training.1600000.processed.noemoticon.csv.shuffled > "$fout"
done
