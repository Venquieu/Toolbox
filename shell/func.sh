# Environment variables
VENV=~/.venv

myenv () {
    action=$1
    name=$2

    if [[ $action == "activate" ]]; then
        source $VENV/$name/bin/activate
    elif [[ $action == "create" ]]; then
        python -m venv --system-site-packages $VENV/$name
    elif [[ $action == "list" ]]; then
        ls $VENV
    elif [[ $action == "remove" ]]; then
        rm -rf $VENV/$name
    fi
}

killer () {
    command=$1
    echo "process to be killed:"
    echo $(ps aux | grep "$command" | grep -v grep)

    echo "Sure to kill?(y/n):"
    read confirm
    if [[ $confirm == "y" ]]; then
        kill -9 $(ps aux | grep "$command" | grep -v grep | awk '{print $2}')
    else
        echo "Quit without killing."
    fi
}
