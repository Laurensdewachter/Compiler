



# run src.main for every file in input
mkdir -p output
for file in input/*.c; do
    echo "Running src.main on $file"
    python -m src.main --input $file --render_ast output/$(basename $file).ast --target_llvm output/$(basename $file).ll 2> output/$(basename $file).log
done