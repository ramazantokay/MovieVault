from customer import Customer

import psycopg2

from config import read_config
from messages import *

"""
    Splits given command string by spaces and trims each token.
    Returns token list.
"""


def tokenize_command(command):
    tokens = command.split(" ")
    return [t.strip() for t in tokens]


class Mp2Client:
    def __init__(self, config_filename):
        self.db_conn_params = read_config(filename=config_filename, section="postgresql")
        self.conn = None

    """
        Connects to PostgreSQL database and returns connection object.
    """

    def connect(self):
        self.conn = psycopg2.connect(**self.db_conn_params)
        self.conn.autocommit = False

    """
        Disconnects from PostgreSQL database.
    """

    def disconnect(self):
        self.conn.close()

    """
        Prints list of available commands of the software.
    """

    def help(self):
        # prints the choices for commands and parameters
        print("\n*** Please enter one of the following commands ***")
        print("> help")
        print("> sign_up <email> <password> <first_name> <last_name> <plan_id>")
        print("> sign_in <email> <password>")
        print("> sign_out")
        print("> show_plans")
        print("> show_subscription")
        print("> subscribe <plan_id>")
        print("> watch <movie_id_1> <movie_id_2> <movie_id_3> ... <movie_id_n>")
        print("> search_for_movies <keyword_1> <keyword_2> <keyword_3> ... <keyword_n>")
        print("> suggest_movies")
        print("> quit")

    """
        Saves customer with given details.
        - Return type is a tuple, 1st element is a boolean and 2nd element is the response message from messages.py.
        - If the operation is successful, commit changes and return tuple (True, CMD_EXECUTION_SUCCESS).
        - If any exception occurs; rollback, do nothing on the database and return tuple (False, CMD_EXECUTION_FAILED).
    """

    def sign_up(self, email, password, first_name, last_name, plan_id): #

        sign_up_customer_query = "insert into customers (email, password, firstname, lastname, sessioncount, planid) values (%s,%s,%s,%s,%s,%s);"
        check_customer_query = "select * from customers c where c.email = %s;"

        try:
            cursor = self.conn.cursor()
            cursor.execute(check_customer_query, (email,))
            customer_records = cursor.fetchall()
            # if there exists any user with same email address, don't sign up
            if customer_records:
                cursor.close
                return False, CMD_EXECUTION_FAILED
            else:
                cursor.execute(sign_up_customer_query, (email, password, first_name, last_name, 0, plan_id))
                self.conn.commit()
                cursor.close()
                return True, CMD_EXECUTION_SUCCESS
        except (Exception, psycopg2.DatabaseError) as error:
            self.conn.rollback()
            cursor.close()
            return False, CMD_EXECUTION_FAILED

    """
        Retrieves customer information if email and password is correct and customer's sessionCount < maxParallelSessions.
        - Return type is a tuple, 1st element is a customer object and 2nd element is the response message from messages.py.
        - If email or password is wrong, return tuple (None, USER_SIGNIN_FAILED).
        - If sessionCount < maxParallelSessions, commit changes (increment sessionCount) and return tuple (customer, CMD_EXECUTION_SUCCESS).
        - If sessionCount >= maxParallelSessions, return tuple (None, USER_ALL_SESSIONS_ARE_USED).
        - If any exception occurs; rollback, do nothing on the database and return tuple (None, USER_SIGNIN_FAILED).
    """

    def sign_in(self, email, password): #

        customer_query = "select * from customers c where c.email= %s and c.password =%s;"
        plan_query = "select * from plans p where p.planid = %s;"
        update_customer_query = "update customers c set sessioncount = %s where c.email=%s and c.password=%s;"

        try:
            cursor = self.conn.cursor()
            cursor.execute(customer_query, (email, password,))
            customer_records = cursor.fetchall()
            if len(customer_records) == 1:
                cursor.execute(plan_query, (customer_records[0][6],))
                plan_records = cursor.fetchall()
                max_session_count_for_the_plan = plan_records[0][3]
                if customer_records[0][5] < max_session_count_for_the_plan:
                    cursor.execute(update_customer_query, (customer_records[0][5] + 1, email, password,))
                    customer_object = Customer(customer_records[0][0], customer_records[0][1], customer_records[0][3],
                                               customer_records[0][4], customer_records[0][5] + 1, customer_records[0][6])
                    self.conn.commit()
                    cursor.close()
                    return customer_object, CMD_EXECUTION_SUCCESS
                else:
                    self.conn.rollback()
                    cursor.close()
                    return None, USER_ALL_SESSIONS_ARE_USED
        except (Exception, psycopg2.DatabaseError) as error:
            self.conn.rollback()
            cursor.close()
            return None, USER_SIGNIN_FAILED
        # if e-mail or password is wrong
        self.conn.rollback()
        cursor.close()
        return None, USER_SIGNIN_FAILED

    """
        Signs out from given customer's account.
        - Return type is a tuple, 1st element is a boolean and 2nd element is the response message from messages.py.
        - Decrement sessionCount of the customer in the database.
        - If the operation is successful, commit changes and return tuple (True, CMD_EXECUTION_SUCCESS).
        - If any exception occurs; rollback, do nothing on the database and return tuple (False, CMD_EXECUTION_FAILED).
    """

    def sign_out(self, customer): #

        update_customer_query = "update customers set sessioncount = %s where customerid=%s;"

        try:
            cursor = self.conn.cursor()
            session_count = int(customer.session_count) - 1
            customer.session_count = customer.session_count - 1
            cursor.execute(update_customer_query, (session_count, customer.customer_id,))
            self.conn.commit()
            cursor.close()
            return True, CMD_EXECUTION_SUCCESS
        except (Exception, psycopg2.DatabaseError) as error:
            self.conn.rollback()
            cursor.close()
            return False, CMD_EXECUTION_FAILED

    """
        Quits from program.
        - Return type is a tuple, 1st element is a boolean and 2nd element is the response message from messages.py.
        - Remember to sign authenticated user out first.
        - If the operation is successful, commit changes and return tuple (True, CMD_EXECUTION_SUCCESS).
        - If any exception occurs; rollback, do nothing on the database and return tuple (False, CMD_EXECUTION_FAILED).
    """

    def quit(self, customer): # check again
        try:
            self.sign_out(customer)
            return True, CMD_EXECUTION_SUCCESS
        except (Exception, psycopg2.DatabaseError) as error:
            return False, CMD_EXECUTION_FAILED

    """
        Retrieves all available plans and prints them.
        - Return type is a tuple, 1st element is a boolean and 2nd element is the response message from messages.py.
        - If the operation is successful; print available plans and return tuple (True, CMD_EXECUTION_SUCCESS).
        - If any exception occurs; return tuple (False, CMD_EXECUTION_FAILED).
        
        Output should be like:
        #|Name|Resolution|Max Sessions|Monthly Fee
        1|Basic|720P|2|30
        2|Advanced|1080P|4|50
        3|Premium|4K|10|90
    """

    def show_plans(self): #

        show_all_plans_query = "select * from plans p;"

        try:
            cursor = self.conn.cursor()
            cursor.execute(show_all_plans_query)
            all_plans_records = cursor.fetchall()

            if not all_plans_records:
                cursor.close()
                return False, CMD_EXECUTION_FAILED

            if len(all_plans_records) > 0:
                print("#|Name|Resolution|Max Sessions|Monthly Fee")
                for plan in all_plans_records:
                    print(str(plan[0]) + "|" + str(plan[1]) + "|" + str(plan[2]) + "|" + str(plan[3]) + "|" + str(plan[4]))
                self.conn.commit()
                cursor.close()
                return True, CMD_EXECUTION_SUCCESS
        except (Exception, psycopg2.DatabaseError) as error:
            self.conn.rollback()
            cursor.close()
            return False, CMD_EXECUTION_FAILED
        self.conn.rollback()
        cursor.close()
        return False, CMD_EXECUTION_FAILED

    """
        Retrieves authenticated user's plan and prints it. 
        - Return type is a tuple, 1st element is a boolean and 2nd element is the response message from messages.py.
        - If the operation is successful; print the authenticated customer's plan and return tuple (True, CMD_EXECUTION_SUCCESS).
        - If any exception occurs; return tuple (False, CMD_EXECUTION_FAILED).

        Output should be like:
        #|Name|Resolution|Max Sessions|Monthly Fee
        1|Basic|720P|2|30
    """

    def show_subscription(self, customer): #

        show_subscription_query = "select * from plans p where p.planid =%s;"

        try:
            cursor = self.conn.cursor()
            cursor.execute(show_subscription_query, (customer.plan_id,))
            plan_records = cursor.fetchall()
            if len(plan_records) == 1:
                print("#|Name|Resolution|Max Sessions|Monthly Fee")
                print(str(plan_records[0][0])+"|"+str(plan_records[0][1])+"|"+str(plan_records[0][2])+"|"+str(plan_records[0][3])+"|"+str(plan_records[0][4]))
                self.conn.commit()
                cursor.close()
                return True, CMD_EXECUTION_SUCCESS
        except (Exception, psycopg2.DatabaseError) as error:
            self.conn.rollback()
            cursor.close()
            return False, CMD_EXECUTION_FAILED
        self.conn.rollback()
        cursor.close()
        return False, CMD_EXECUTION_FAILED

    """
        Insert customer-movie relationships to watched table if not exists in watched table.
        - Return type is a tuple, 1st element is a boolean and 2nd element is the response message from messages.py.
        - If a customer-movie relationship already exists, do nothing on the database and return (True, CMD_EXECUTION_SUCCESS).
        - If the operation is successful, commit changes and return tuple (True, CMD_EXECUTION_SUCCESS).
        - If any one of the movie ids is incorrect; rollback, do nothing on the database and return tuple (False, CMD_EXECUTION_FAILED).
        - If any exception occurs; rollback, do nothing on the database and return tuple (False, CMD_EXECUTION_FAILED).
    """

    def watch(self, customer, movie_ids): #

        insert_watched_movie_query = "insert into watched (customerid, movieid) values(%s, %s);"
        check_a_movie_exists_query = "select * from movies m where m.movieid = %s;"
        check_a_movie_watched_before_query = "select * from watched w where w.customerid = %s and w.movieid = %s;"

        try:
            cursor = self.conn.cursor()
            for movie_id in movie_ids:
                cursor.execute(check_a_movie_exists_query, (movie_id,))
                movie_exists_records = cursor.fetchall()
                if len(movie_exists_records) > 0:
                    cursor.execute(check_a_movie_watched_before_query, (customer.customer_id, movie_id,))
                    watched_movie_exists_records = cursor.fetchall()
                    if len(watched_movie_exists_records) == 0:
                        cursor.execute(insert_watched_movie_query, (customer.customer_id, movie_id,))
                    else:
                        continue
                else:
                    self.conn.rollback()
                    cursor.close()
                    return False, CMD_EXECUTION_FAILED
            self.conn.commit()
            cursor.close()
            return True, CMD_EXECUTION_SUCCESS
        except (Exception, psycopg2.DatabaseError) as error:
            self.conn.rollback()
            cursor.close()
            return False, CMD_EXECUTION_FAILED

    """
        Subscribe authenticated customer to new plan.
        - Return type is a tuple, 1st element is a customer object and 2nd element is the response message from messages.py.
        - If target plan does not exist on the database, return tuple (None, SUBSCRIBE_PLAN_NOT_FOUND).
        - If the new plan's maxParallelSessions < current plan's maxParallelSessions, return tuple (None, SUBSCRIBE_MAX_PARALLEL_SESSIONS_UNAVAILABLE).
        - If the operation is successful, commit changes and return tuple (customer, CMD_EXECUTION_SUCCESS).
        - If any exception occurs; rollback, do nothing on the database and return tuple (None, CMD_EXECUTION_FAILED).
    """

    def subscribe(self, customer, plan_id): #

        plan_query = "select * from plans p where p.planid = %s;"
        update_customer_query = "update customers c set planid = %s where c.customerid = %s"

        try:
            cursor = self.conn.cursor()
            cursor.execute(plan_query, (plan_id,))
            plan_records = cursor.fetchone()
            if plan_records:
                new_plan = plan_records
            else:
                self.conn.rollback()
                cursor.close()
                return None, SUBSCRIBE_PLAN_NOT_FOUND

            cursor.execute(plan_query, (customer.plan_id,))
            old_plan_records = cursor.fetchone()

            if new_plan[3] >= old_plan_records[3]:
                cursor.execute(update_customer_query, (plan_id, customer.customer_id))
                customer.plan_id = plan_id
                self.conn.commit()
                cursor.close()
                return customer, CMD_EXECUTION_SUCCESS
            else:
                self.conn.rollback()
                cursor.close()
                return None, SUBSCRIBE_MAX_PARALLEL_SESSIONS_UNAVAILABLE

        except(Exception, psycopg2.DatabaseError) as error:
            self.conn.rollback()
            cursor.close()
            return False, CMD_EXECUTION_FAILED
        self.conn.rollback()
        cursor.close()
        return False, CMD_EXECUTION_FAILED

    """
        Searches for movies with given search_text.
        - Return type is a tuple, 1st element is a boolean and 2nd element is the response message from messages.py.
        - Print all movies whose titles contain given search_text IN CASE-INSENSITIVE MANNER.
        - If the operation is successful; print movies found and return tuple (True, CMD_EXECUTION_SUCCESS).
        - If any exception occurs; return tuple (False, CMD_EXECUTION_FAILED).
        
        Output should be like:
        Id|Title|Year|Rating|Votes|Watched
        "tt0147505"|"Sinbad: The Battle of the Dark Knights"|1998|2.2|149|0
        "tt0468569"|"The Dark Knight"|2008|9.0|2021237|1
        "tt1345836"|"The Dark Knight Rises"|2012|8.4|1362116|0
        "tt3153806"|"Masterpiece: Frank Millers The Dark Knight Returns"|2013|7.8|28|0
        "tt4430982"|"Batman: The Dark Knight Beyond"|0|0.0|0|0
        "tt4494606"|"The Dark Knight: Not So Serious"|2009|0.0|0|0
        "tt4498364"|"The Dark Knight: Knightfall - Part One"|2014|0.0|0|0
        "tt4504426"|"The Dark Knight: Knightfall - Part Two"|2014|0.0|0|0
        "tt4504908"|"The Dark Knight: Knightfall - Part Three"|2014|0.0|0|0
        "tt4653714"|"The Dark Knight Falls"|2015|5.4|8|0
        "tt6274696"|"The Dark Knight Returns: An Epic Fan Film"|2016|6.7|38|0
    """

    def search_for_movies(self, customer, search_text): #
        # TODO: Implement this function
        search_movies_query = "select * from movies m where m.originaltitle ILIKE %s order by m.movieid; "
        search_watched_movies_query = "select * from watched w where w.customerid = %s and w.movieid = %s;"

        try:
            cursor = self.conn.cursor()
            cursor.execute(search_movies_query, ('%' + search_text + '%',))
            movies_records = cursor.fetchall()
            print("Id|Title|Year|Rating|Votes|Watched")
            for movie in movies_records:
                cursor.execute(search_watched_movies_query, (customer.customer_id, movie[0],))
                watched_movies_records = cursor.fetchall()
                if len(watched_movies_records) > 0:
                    print(str(movie[0]) + "|" + str(movie[1]) + "|" + str(movie[2]) + "|" + str(movie[3]) + "|" + str(movie[4]) + "|1")
                else:
                    print(str(movie[0]) + "|" + str(movie[1]) + "|" + str(movie[2]) + "|" + str(movie[3]) + "|" + str(movie[4]) + "|0")
            self.conn.commit()
            cursor.close()
            return True, CMD_EXECUTION_SUCCESS
        except (Exception, psycopg2.DatabaseError) as error:
            self.conn.rollback()
            cursor.close()
            return False, CMD_EXECUTION_FAILED

    """
        Suggests combination of these movies:
            1- Find customer's genres. For each genre, find movies with most numVotes among the movies that the customer didn't watch.
            
            2- Find top 10 movies with most numVotes and highest averageRating, such that these movies are released 
            after 2010 ( [2010, today) ) and the customer didn't watch these movies.
            (descending order for numVotes, descending order for averageRating)
            
            3- Find top 10 movies with numVotes higher than the average numVotes of movies that the customer watched.
            Disregard the movies that the customer didn't watch.
            (descending order for numVotes)
            
        - Return type is a tuple, 1st element is a boolean and 2nd element is the response message from messages.py.    
        - Output format and return format are same with search_for_movies.
        - Order these movies by their movie id, in ascending order at the end.
        - If the operation is successful; print movies suggested and return tuple (True, CMD_EXECUTION_SUCCESS).
        - If any exception occurs; return tuple (False, CMD_EXECUTION_FAILED).
    """

    def suggest_movies(self, customer):#

        search_genre_query = "select distinct g.genre from watched w, movies m, genres g where w.customerid= %s and  w.movieid = m.movieid and g.movieid = m.movieid;"
        step1_query = "select m.movieid, m.originaltitle, m.startyear, m.averagerating, m.numvotes from movies m, genres g where m.movieid = g.movieid and g.genre = %s and m.movieid not in (select w.movieid from watched w where w.customerid = %s) order by m.numvotes desc limit 1;"
        step2_query = "select * from movies m where m.startyear >= 2010 and m.movieid not in (select w.movieid from watched w where w.customerid = %s) order by m.numvotes desc, m.averagerating desc limit 10;"
        search_average_watched_movie_query = "select avg(m.numvotes) from watched w, movies m where w.customerid = %s and m.movieid = w.movieid;"
        step3_query ="select * from movies m where m.numvotes > %s and m.movieid not in (select w.movieid from watched w where w.customerid =%s) order by m.numvotes desc limit 10;"

        try:
            output_movie = set()

            cursor = self.conn.cursor()
            cursor.execute(search_genre_query, (customer.customer_id,))
            genre_records = cursor.fetchall()

            for genre in genre_records:
                cursor.execute(step1_query, (genre, customer.customer_id,))
                movie_record = cursor.fetchone()
                output_movie.add(movie_record)

            cursor.execute(step2_query, (customer.customer_id,))
            top_10_movies_records = cursor.fetchall()
            for movie in top_10_movies_records:
                output_movie.add(movie)

            cursor.execute(search_average_watched_movie_query, (customer.customer_id,))
            average_votes = cursor.fetchall()

            cursor.execute(step3_query, (float(average_votes[0][0]), customer.customer_id,))
            top_10_movies_high_average_records = cursor.fetchall()
            for movie in top_10_movies_high_average_records:
                output_movie.add(movie)

            output_movie = sorted(output_movie, key=lambda movie: movie[0], reverse=False)
            print("Id|Title|Year|Rating|Votes")
            for movie in output_movie:
                print(str(movie[0]) + "|" + str(movie[1]) + "|" + str(movie[2]) + "|" + str(movie[3]) + "|"+ str(movie[4]))

            self.conn.commit()
            cursor.close()
            return True, CMD_EXECUTION_SUCCESS
        except (Exception, psycopg2.DatabaseError) as error:
            self.conn.rollback()
            cursor.close
            return False, CMD_EXECUTION_FAILED
