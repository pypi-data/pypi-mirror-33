from zcy_parser import parser


def main():
    try:
        parser.parse_args()
    except KeyboardInterrupt:
        pass


if __name__ == '__main__':
    main()