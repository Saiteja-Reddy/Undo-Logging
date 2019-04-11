if [ "$#" -eq 2 ]; then
    # echo "Logging"
    python 201564086_1.py "$1" "$2"
elif [ "$#" -eq 1 ]
	then
    # echo "Undo Recovery"
    python 201564086_2.py "$1"
else
	echo "Error check arguments"
fi