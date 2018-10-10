"""Extract from a log file speeds and compute average speed and batch time."""
from __future__ import print_function
import re
import sys


model_titles = {
    "alexnet_owt": "AlexNetOWT", "googlenet": "GoogleNet", "inception_resnet_v2": "InceptionResNetV2",
    "inception3": "InceptionV3", "inception4": "InceptionV4", "overfeat": "Overfeat",
    "resnet18": "ResNet18", "resnet34": "ResNet34", "resnet50": "ResNet50", "resnet101": "ResNet101", "resnet152": "ResNet152",
    "vgg11": "VGG11", "vgg13": "VGG13", "vgg16": "VGG16", "vgg19": "VGG19",
    "xception": "Xception"
}


def main():
    """Main function."""
    # Get input parameters
    fname = sys.argv[1]
    model = sys.argv[2]
    effective_batch = int(sys.argv[3])
    # Load log file content
    with open(fname) as logfile:
        lines = [line.strip() for line in logfile]
    # Define possible parser states
    state = type('Enum', (), {'SEARCH': 1, 'PROCESS': 2})
    header = 'Step[\t ]+Epoch[\t ]+Img/sec[\t ]+Loss[\t ]+LR'
    # Parse content
    speeds = []
    parser_state = state.SEARCH
    for line in lines:
        if parser_state == state.SEARCH:
            parser_state = state.PROCESS if re.match(header, line) else state.SEARCH
            continue
        line = line.split()
        if len(line) != 6:
            break
        try:
            line = [float(col) for col in line]
            speeds.append(line[2])
        except ValueError:
            break
    # Find average speed/processing time
    if len(speeds) < 20:
	# It's better to remove first two points even if number of iterations was small.
	if len(speeds) >= 5:
	    speeds = speeds[2:]
	print(
	    "[WARNING] Number of performance points is too low (%d). "\
	    "I will use almost all points to compute average. Better algorithm "\
	    "exists."  % len(speeds)
	)
    else:
	speeds = speeds[10:]
    # Do some logging
    if model in model_titles:
	print("__exp.model_title__=\"%s\"" % model_titles[model])
    if len(speeds) > 0:
        speed = sum(speeds) / len(speeds)
        batch_time = 1000.0 / (speed / effective_batch)
        # Print results
        print("__results.throughput__=%f" % speed)
        print("__results.time__=%f" % batch_time)
        print("__exp.status__=\"success\"")
    else:
        print("__exp.status__=\"failure\"")
        print("__exp.status_msg__=\"No results have been found in this log file\"")

if __name__ == '__main__':
    main()
