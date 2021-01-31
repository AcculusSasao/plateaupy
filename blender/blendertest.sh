#!/bin/sh

# preparation:
#   download 2.91.2    https://www.blender.org/download/
# specify the directory path
BLENDER=~/blender

# test script
TEST_SCRIPT=blender/blendertest.py
# blender bin
BLENDER_BIN=$BLENDER/blender
# blender python
BLENDER_PYTHON=$BLENDER/2.91/python/bin/python3.7m

if [ $# != 0 ]; then
	echo
	echo check Blender path : $BLENDER
	echo
	# install pip and modules
	$BLENDER_PYTHON -m ensurepip
	BLENDER_PIP=$BLENDER/2.91/python/bin/pip3
	$BLENDER_PIP install --upgrade pip
	$BLENDER_PIP install lxml open3d opencv-python
else
	# run
	# https://docs.blender.org/manual/en/dev/advanced/command_line/arguments.html#python-options
	$BLENDER_BIN --python $TEST_SCRIPT --python-use-system-env
fi
