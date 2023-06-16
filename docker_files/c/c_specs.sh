#!/bin/bash

show_help() {
    echo "usage:  $BASH_SOURCE --timeout <seconds> --attempt <id> --test <id> --contest <id> --fsize <KiB> --compile_flags <compile flags> --linkage_flags <linkage flags> --run_arguments <run arguments> --leak <0|1>";
    echo "                     --input1 - is input 1 .";
    echo "                     --input2 - is input 2 .";
    echo "                     --input3 - is input 3 .";
}

# Read command line options
declare -a ARGUMENT_LIST=(
    "timeout"
    "attempt"
    "test"
	"contest"
	"fsize"
	"compile_flags"
	"linkage_flags"
	"run_arguments"
	"check_leak"
)

# read arguments
opts=$(getopt \
    --longoptions "$(printf "%s:," "${ARGUMENT_LIST[@]}")" \
    --name "$(basename "$0")" \
    --options "" \
    -- "$@"
)

eval set --$opts

while true; do
    case "$1" in
    h)
        show_help
        exit 0
        ;;
    --timeout)  
        shift
        timeout=$1
        ;;
    --attempt)  
        shift
        attempt=$1
        ;;
    --test)  
        shift
        test=$1
        ;;
    --contest)  
        shift
        contest=$1
        ;;
    --fsize)  
        shift
        fsize=$1
        ;;
    --compile_flags)  
        shift
        compile_flags=$1
        ;;
    --linkage_flags)  
        shift
        linkage_flags=$1
        ;;
    --run_arguments)  
        shift
        run_arguments=$1
        ;;
    --check_leak)  
        shift
        leak=$1
        ;;												
      --)
        shift
        break
        ;;
    esac
    shift
done


echo "timeout = $timeout";
echo "attempt_id = $attempt";
echo "test_id = $test";
echo "contest_id = $contest";
echo "fsize = $fsize";
echo "compile_flags = $compile_flags";
echo "linkage_flags = $linkage_flags";
echo "run_arguments = $run_arguments";
echo "check_leak = $leak";

set -e
#trap 'catch erro par2 par3' EXIT

catch() {
  echo "== $1 == Erro catched"

  if [ "$1" != "0" ]; then

  case $1 in
	1)
		echo "SIGHUP	1	Exit	Hangup" > /disco/submission_results/$2/$3.test
		;;
	2)
		echo "SIGINT	2	Exit	Interrupt" > /disco/submission_results/$2/$3.test
		;;
	3)
		echo "SIGQUIT	3	Core	Quit" > /disco/submission_results/$2/$3.test
		;;
	4)
		echo "SIGILL Core	Illegal Instruction" > /disco/submission_results/$2/$3.test 
		;;
	5)
		echo "SIGTRAP Core	Trace/Breakpoint Trap" > /disco/submission_results/$2/$3.test 
		;;
	6)
		echo "SIGABRT Core	Abort" > /disco/submission_results/$2/$3.test 
		;;
	7)
		echo "SIGEMT Core	Emulation Trap" > /disco/submission_results/$2/$3.test 
		;;
	8)
		echo "SIGFPE Core	Arithmetic Exception" > /disco/submission_results/$2/$3.test 
		;;
	9)
		echo "SIGKILL Exit	Killed" > /disco/submission_results/$2/$3.test 
		;;
	10)
		echo "SIGBUS Core	Bus Error" > /disco/submission_results/$2/$3.test 
		;;
	11)
		echo "SIGSEGV Core	Segmentation Fault" > /disco/submission_results/$2/$3.test 
		;;
	12)
		echo "SIGSYS Core	Bad System Call" > /disco/submission_results/$2/$3.test 
		;;
	13)
		echo "SIGPIPE Exit	Broken Pipe" > /disco/submission_results/$2/$3.test 
		;;
	14)
		echo "SIGALRM Exit	Alarm Clock" > /disco/submission_results/$2/$3.test 
		;;
	15)
		echo "SIGTERM Exit	Terminated" > /disco/submission_results/$2/$3.test 
		;;
	16)
		echo "SIGUSR1 Exit	User Signal 1" > /disco/submission_results/$2/$3.test 
		;;
	17)
		echo "SIGUSR2 Exit	User Signal 2" > /disco/submission_results/$2/$3.test 
		;;
	18)
		echo "SIGCHLD Ignore	Child Status" > /disco/submission_results/$2/$3.test 
		;;
	19)
		echo "SIGPWR Ignore	Power Fail/Restart" > /disco/submission_results/$2/$3.test 
		;;
	20)
		echo "SIGWINCH Ignore	Window Size Change" > /disco/submission_results/$2/$3.test 
		;;
	21)
		echo "SIGURG Ignore	Urgent Socket Condition" > /disco/submission_results/$2/$3.test 
		;;
	22)
		echo "SIGPOLL Ignore	Socket I/O Possible" > /disco/submission_results/$2/$3.test 
		;;
	23)
		echo "SIGSTOP		Stop	Stopped (signal)"> /disco/submission_results/$2/$3.test 
		;;
	24)
		echo "SIGTSTP		Stop	Stopped (user)" > /disco/submission_results/$2/$3.test 
		;;
	25)
		echo "SIGCONT		Ignore	Continued" > /disco/submission_results/$2/$3.test 
		;;
	26)
		echo "SIGTTIN		Stop	Stopped (tty input)" > /disco/submission_results/$2/$3.test 
		;;
	27)
		echo "SIGTTOU		Stop	Stopped (tty output)" > /disco/submission_results/$2/$3.test 
		;;
	28)
		echo "SIGVTALRM	Exit	Virtual Timer Expired" > /disco/submission_results/$2/$3.test 
		;;
	29)
		echo "SIGPROF		Exit	Profiling Timer Expired" > /disco/submission_results/$2/$3.test 
		;;
	30)
		echo "SIGXCPU		Core	CPU time limit exceeded" > /disco/submission_results/$2/$3.test 
		;;
	31)
		echo "SIGXFSZ		Core	File size limit exceeded" > /disco/submission_results/$2/$3.test 
		;;
	32)
		echo "SIGWAITING	Ignore	All LWPs blocked" > /disco/submission_results/$2/$3.test 
		;;
	33)
		echo "SIGLWP		Ignore	Virtual Interprocessor Interrupt for Threads Library" > /disco/submission_results/$2/$3.test 
		;;
	34)
		echo "SIGAIO		Ignore	Asynchronous I/O" > /disco/submission_results/$2/$3.test 
		;;
	77)
		echo "LEAK		Memory Leak Test: FAILED" > /disco/submission_results/$2/$3.test 
		;;
  esac

	if [ "$1" == "124" ]; then #timeout error code
		echo "Error: Timeout!" > /disco/submission_results/$2/$3.test ;
		fi

		if [ "$1" == "153" ]; then #filesize excceded error code
		  echo "Output is too big"
			echo "Error: Output is too big!" > /disco/submission_results/$2/$3.test ;
		fi

		if [ "$1" == "1" ]; then #compilation error code
			echo "Error" > /disco/submission_results/$2/compilation.result
		fi
		chmod -R 0777 /disco/submission_results/$2/
		cp -r /usr/src/compiled/* /disco/tmp/$2/ 2>/dev/null || :
		chmod -R 0777 /disco/tmp/$2/
		exit 0
    echo "Test error: Unexpected error $1 ocurred"  #> /disco/submission_results/$attempt_id/$test_id.test ; exit 0 #> /disco/submission_results/$attempt_id/$test_id.out ; exit 0
	else
		chmod -R 0777 /disco/submission_results/$2/
		cp -r /usr/src/compiled/* /disco/tmp/$2/ 2>/dev/null || :
		chmod -R 0777 /disco/tmp/$2/
	fi

}

mkdir -p /disco/submission_results/$attempt/
cp -r /disco/tmp/$attempt/* /usr/src/compiled/ 2>/dev/null || :
cp -r /disco/datafiles/$contest/* /usr/src/compiled/ 2>/dev/null  || :
cd /disco/submissions/$attempt/
ulimit -f $fsize
trap 'catch $? $attempt_id' EXIT

echo "Running Static analisys"
cppcheck --enable=all --suppress=missingIncludeSystem . 2> /disco/submission_results/$attempt/static.out

#cppcheck --enable=all --quiet *.c > /disco/submission_results/$attempt/static.out


if [ "$test" == "0" ]; then # Run compilation
  compile.sh $attempt "$compile_flags" "$linkage_flags"
else # Run test
  trap 'catch $? $attempt $test' EXIT
  run.sh $attempt $test $timeout "$run_arguments" "$leak"
#	cd /usr/src/compiled
#	echo "Running Test"
#	echo "/usr/bin/time --quiet -f %U %K %p %e %M %x -o /disco/submission_results/$attempt/$test.time timeout $timeout ./program < /disco/tests/$test/test.in > /disco/submission_results/$attempt/$test.out && echo Ok > /disco/submission_results/$attempt/$test.test"
#	/usr/bin/time --quiet -f "%U %K %p %e %M %x" -o /disco/submission_results/$attempt/$test.time timeout $timeout ./program $run_arguments < /disco/tests/$test/test.in | ascii > /disco/submission_results/$attempt/$test.out && echo "Ok" > /disco/submission_results/$attempt/$test.test
fi
