import epfml.config as config
import epfml.store as store
import epfml.vpn as vpn
from epfml.cli.subcommand import SubCommand


class Store(SubCommand):
    name = "store"

    def define_parser(self, parser):
        parser.add_argument("--user", "-u", type=str, default=config.ldap)

        subparsers = parser.add_subparsers(dest="subcommand", required=True)

        getparser = subparsers.add_parser("get")
        getparser.add_argument("key", type=str)

        unsetparser = subparsers.add_parser("unset")
        unsetparser.add_argument("key", type=str)

        setparser = subparsers.add_parser("set")
        setparser.add_argument("key", type=str)
        setparser.add_argument("value", type=str)

    def main(self, args):
        vpn.assert_connected()
        config.assert_store_is_configured()

        if args.subcommand == "get":
            print(store.get(args.key, user=args.user))

        elif args.subcommand == "set":
            store.set(args.key, args.value, user=args.user)

        elif args.subcommand == "unset":
            store.unset(args.key, user=args.user)
