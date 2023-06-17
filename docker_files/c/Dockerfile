FROM gcc:latest
#FROM ubuntu:latest
#RUN apt-get update && apt-get install -y build-essential
#clang-format clang-tidy clang-tools clang libclang-dev
COPY time /usr/bin/time
COPY ascii /usr/bin/ascii
COPY c_specs.sh /usr/src/c_specs.sh
COPY c_specs.sh /usr/bin/c_specs.sh
COPY ascii /usr/bin/ascii
COPY compile.sh /usr/bin/compile.sh
COPY run.sh /usr/bin/run.sh
RUN mkdir /usr/src/compiled/
RUN apt-get update -y && apt install cppcheck -y
RUN apt-get install -y valgrind

RUN apt-get update && apt-get install -y clang-format clang-tidy clang-tools clang libclang-dev llvm libc++-dev
RUN mkdir /app
# Copy the source code files to the container
COPY detect_global_variables.cpp /app
# Set the working directory
WORKDIR /app
# Compile the program using LLVM
RUN clang++ -std=c++17 detect_global_variables.cpp -o /usr/bin/detect_globals -lclang -I/usr/lib/llvm-14/include/


#RUN rm -rf /usr/include/string.h
#RUN rm -rf /usr/include/stdlib.h
#RUN rm -rf /usr/include/strings.h
#ENTRYPOINT ["sh", "-c", "c_specs.sh ${timeout} ${attempt} ${test} ${contest} ${fsize} ${compile_flags} ${linkage_flags} ${check_leak} ${run_arguments}"]
#CMD c_specs.sh -to=${timeout} -aid=${attempt} ${test} ${contest} ${fsize} ${compile_flags} ${linkage_flags} ${check_leak} ${run_arguments}
#CMD /usr/src/c_specs.sh --timeout ${timeout} --attempt ${attempt} --test ${test} --contest ${contest} --fsize ${fsize} --cflags "${compile_flags}" --lflags "${linkage_flags}" --leak ${check_leak} --runargs "${run_arguments}"
#CMD /usr/src/c_specs.sh
