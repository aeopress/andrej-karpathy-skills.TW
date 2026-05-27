import argparse

parser = argparse.ArgumentParser(description='Greet someone')
parser.add_argument('name', help='Name to greet')
args = parser.parse_args()

message = 'Hello, ' + args.name + '!'
print(message)
