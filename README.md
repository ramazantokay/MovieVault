# MovieVault - Database Management Systems Project

This project is a simple video streaming service application, similar to popular platforms like Netflix and Amazon Prime Video. It utilizes a PostgreSQL database to store and manage video content, customer information, and subscription plans.


## Database

The application uses a PostgreSQL database named "ceng352_mp2_data". The database consists of several tables to store information about `actors`, `directors`, `movies`, `genres`, `customers`, `plans`, and more. The initial database schema and sample data can be found in the "construct db.sql" file.

## Software

The application is implemented in `Python3` and uses the `psycopg2` library to interact with the PostgreSQL database. The source files are located in the "source" directory. The main functionality of the application is implemented in the `mp2.py` file, where you will find functions related to `signing up`, `signing in`, `subscribing to plans`, `watching movies`, and more. The `main.py` file acts as the service layer and should be run to start the application.

## Getting Started

To get started with the application, follow these steps:

1. Clone the repository: `git clone https://github.com/ramazantokay/MovieVault.git`
2. Install the required dependencies: `pip install -r requirements.txt`
3. Set up your PostgreSQL database and import the initial schema and data from the "construct db.sql" file.
4. Import the sample data from the "imdb_data.zip" file.
5. Configure the database connection details in the "database.cfg" file.
6. Run the application: `python main.py`

## Commands

The application supports several commands that can be executed from the command line interface. Some of the available commands include:

- `sign_up`: Create a new customer account.
```
>_ sign_up <email> <password> <first name> <last name> <plan id>
```
- `sign_in`: Sign in to an existing customer account.
```
>_ sign_in <email> <password>
```
- `sign_out`: Sign out from the current customer account.
```
>_ sign_out
```
- `show_plans`: Display a list of available subscription plans.
```
>_ show_plans
```
- `show_subscription`: Show the details of the subscribed plan.
```
>_ show_subscription
```
- `subscribe`: Subscribe to a new plan.
```
>_ subscribe <new plan id>
```
- `watch`: Record the movies watched by the current customer.
```
>_ watch <movie 1 id> <movie 2 id> <movie 3 id> ... <movie N id>
```
- `search_for_movies`: Search for movies based on keywords.
```
>_ search_for_movies <keyword 1> <keyword 2> ... <keyword N>
```
- `suggest_movies`: Get movie suggestions based on the customer's watching history.
```
>_ suggest_movies
```
- `quit`: Exit the application.
```
>_ quit
```

## Disclaimer
Please note that this implementation may contain limitations, potential bugs, and dependencies on external libraries and tools. While efforts have been made to ensure correctness, there is no guarantee of flawless execution. Exercise caution, conduct thorough testing, and adapt the code to your requirements. Report issues on GitHub and contribute to improvements. Use responsibly, validate results, and the authors disclaim liability for any damages or issues arising from the use of this code.

## License
This project is licensed under the MIT License - see the LICENSE file for details.

## Contributing

Contributions are welcome! If you have any suggestions or improvements, feel free to submit a pull request or open an issue in the GitHub repository.
