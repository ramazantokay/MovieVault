from mp2 import Mp2Client, tokenize_command
from validators import *

AUTH_CUSTOMER = None
ANON_CUSTOMER = "ANONYMOUS"
POSTGRESQL_CONFIG_FILE_NAME = "database.cfg"


def print_success_msg(message):
    print(message)


def print_error_msg(message):
    print("ERROR: %s" % message)


def print_customer_info(customer):
    global ANON_CUSTOMER

    if customer:
        print(customer, end=" > ")
    else:
        print(ANON_CUSTOMER, end=" > ")


def main():
    global AUTH_CUSTOMER, POSTGRESQL_CONFIG_FILE_NAME

    client = Mp2Client(config_filename=POSTGRESQL_CONFIG_FILE_NAME)
    client.help()

    while True:
        # print customer information if signed in
        print_customer_info(customer=AUTH_CUSTOMER)

        # get new command from user
        cmd_text = input()
        cmd_tokens = tokenize_command(cmd_text)
        cmd = cmd_tokens[0]

        if cmd == "help":
            client.help()

        elif cmd == "sign_up":
            # validate command
            validation_result, validation_message = sign_up_validator(AUTH_CUSTOMER, cmd_tokens)

            if validation_result:
                client.connect()
                _, arg_email, arg_password, arg_first_name, arg_last_name, arg_plan_id = cmd_tokens

                # sign up
                exec_status, exec_message = client.sign_up(email=arg_email, password=arg_password,
                                                            first_name=arg_first_name, last_name=arg_last_name,
                                                            plan_id=arg_plan_id)

                client.disconnect()

                # print message
                if exec_status:
                    print_success_msg(exec_message)
                else:
                    print_error_msg(exec_message)

            else:
                print_error_msg(validation_message)

        elif cmd == "sign_in":
            # validate command
            validation_result, validation_message = sign_in_validator(AUTH_CUSTOMER, cmd_tokens)

            if validation_result:
                _, arg_email, arg_password = cmd_tokens

                client.connect()
                customer, exec_message = client.sign_in(email=arg_email, password=arg_password)

                if customer:
                    AUTH_CUSTOMER = customer
                    print_success_msg(exec_message)

                else:
                    print_error_msg(exec_message)

            else:
                print_error_msg(validation_message)

        elif cmd == "sign_out":

            # validate command
            validation_result, validation_message = sign_out_validator(AUTH_CUSTOMER, cmd_tokens)

            if validation_result:
                exec_status, exec_message = client.sign_out(customer=AUTH_CUSTOMER)

                if exec_status:
                    AUTH_CUSTOMER = None
                    client.disconnect()
                    print_success_msg(exec_message)

                else:
                    print_error_msg(exec_message)

            else:
                print_error_msg(validation_message)

        elif cmd == "quit":

            # validate command
            validation_result, validation_message = quit_validator(cmd_tokens)

            if validation_result:

                exec_status, exec_message = client.quit(customer=AUTH_CUSTOMER)

                if exec_status:
                    break
                else:
                    print_error_msg(exec_message)

            else:
                print_error_msg(validation_message)

        elif cmd == "show_plans":
            # validate command
            validation_result, validation_message = show_plans_validator(AUTH_CUSTOMER, cmd_tokens)

            if validation_result:
                exec_status, exec_message = client.show_plans()

                if not exec_status:
                    print_error_msg(exec_message)

            else:
                print_error_msg(validation_message)

        elif cmd == "show_subscription":
            # validate command
            validation_result, validation_message = show_subscription_validator(AUTH_CUSTOMER, cmd_tokens)

            if validation_result:
                exec_status, exec_message = client.show_subscription(customer=AUTH_CUSTOMER)

                if not exec_status:
                    print_error_msg(exec_message)

            else:
                print_error_msg(validation_message)

        elif cmd == "watch":

            # validate command
            validation_result, validation_message = watch_validator(AUTH_CUSTOMER, cmd_tokens)

            if validation_result:
                exec_status, exec_message = client.watch(customer=AUTH_CUSTOMER, movie_ids=cmd_tokens[1:])

                if exec_status:
                    print_success_msg(exec_message)
                else:
                    print_error_msg(exec_message)

            else:
                print_error_msg(validation_message)

        elif cmd == "subscribe":
            # validate command
            validation_result, validation_message = subscribe_validator(AUTH_CUSTOMER, cmd_tokens)

            if validation_result:
                _, arg_plan_id = cmd_tokens

                customer, exec_message = client.subscribe(customer=AUTH_CUSTOMER, plan_id=arg_plan_id)

                if customer:
                    AUTH_CUSTOMER = customer
                    print_success_msg(exec_message)

                else:
                    print_error_msg(exec_message)

            else:
                print_error_msg(validation_message)

        elif cmd == "search_for_movies":
            # validate command
            validation_result, validation_message = search_for_movies_validator(AUTH_CUSTOMER, cmd_tokens)

            if validation_result:
                arg_search_text = " ".join(cmd_tokens[1:])

                exec_status, exec_message = client.search_for_movies(customer=AUTH_CUSTOMER, search_text=arg_search_text)

                if not exec_status:
                    print_error_msg(exec_message)

            else:
                print_error_msg(validation_message)

        elif cmd == "suggest_movies":
            # validate command
            validation_result, validation_message = suggest_movies_validator(AUTH_CUSTOMER, cmd_tokens)

            if validation_result:
                exec_status, exec_message = client.suggest_movies(customer=AUTH_CUSTOMER)

                if not exec_status:
                    print_error_msg(exec_message)

            else:
                print_error_msg(validation_message)

        elif cmd == "":
            pass

        else:
            print_error_msg(messages.CMD_UNDEFINED)


if __name__ == '__main__':
    main()
