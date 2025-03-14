mkdir -p build
cd build
rm CMakeCache.txt

cmake \
    -DCMAKE_EXPORT_COMPILE_COMMANDS=ON \
    -DCMAKE_C_FLAGS="-O0 --coverage --save-temps" \
    -DBUILD_SHARED_LIBS=OFF \
    ../

# Check if failed
if [ $? -ne 0 ]; then
  exit 1
fi
