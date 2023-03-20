import os
import argparse
import logging
from rich.console import Console
from rich.text import Text
from dotenv import load_dotenv
import openai
import time
import random
from argparse import HelpFormatter
import json

# Load resources from JSON files
with open("engine_descriptions.json", "r") as f:
    ENGINE_DESCRIPTIONS = json.load(f)

with open("haikus.json", "r") as f:
    haikus = json.load(f)

with open("hacking_quotes.json", "r") as f:
    hacking_quotes = json.load(f)

# Initialize console with a fixed width of 60
console = Console(width=60)

# Load environment variables from .env file and set OpenAI API key
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# Initialize the history list to store user input and GPT responses
history = []

# Custom help formatter for argparse
class ColoredHelpFormatter(HelpFormatter):
    def __init__(self, *args, **kwargs):
        self.option_color = "\033[93m"
        self.usage_color = "\033[95m"
        super().__init__(*args, **kwargs)

    def _get_help_string(self, action):
        help_str = action.help
        if help_str.startswith("Usage:"):
            return f"\033[95m{help_str}\033[0m"
        return help_str

    def _split_lines(self, text, width):
        if (
            text.startswith("Available options:")
            or text.startswith("Mode selection:")
            or text.startswith("Logging verbosity:")
        ):
            return [text]
        return super()._split_lines(text, width)

    def _format_action(self, action):
        parts = super()._format_action(action)
        if action.option_strings:
            parts = f"\033[93m{parts}\033[0m"
        return parts


# Set up command line arguments and logging
def setup_arguments_and_logging():
    console = Console(width=80)

    load_dotenv()
    openai.api_key = os.getenv("OPENAI_API_KEY")

    # Update the parser description
    engine_descriptions = " - ".join(
        [f"{engine}{desc}" for engine, desc in ENGINE_DESCRIPTIONS.items()]
    )
    parser_description = f"sentAI ChatGPT Terminal\n\n"
    usage = f"Usage:\n  python innit.py [-h] [-i] [-e ENGINE] [-t MAX_TOKENS] [-T TEMPERATURE] [-m MODE] [-v VERBOSITY] [-TT TOP_P] [-n NUM_SUGGESTIONS]\n\nExample commands:\n  python innit.py -h  # Display help message\n  python innit.py -i -e davinci  # Start in interactive"
    # Initialize the parser with the updated description
    parser = argparse.ArgumentParser(
        description=parser_description, formatter_class=ColoredHelpFormatter
    )

    parser.add_argument(
        "-i", "--interactive", action="store_true", help="Enable interactive mode"
    )
    parser.add_argument(
        "-e",
        "--engine",
        default="text-davinci-003",
        help=f"OpenAI engine\nAvailable options: \033[91m{engine_descriptions}\033[0m",
    )
    parser.add_argument(
        "-t",
        "--max_tokens",
        type=int,
        default=800,
        help="Max tokens for response (maximum: 4096)",
    )
    parser.add_argument(
        "-T",
        "--temperature",
        type=float,
        default=0.8,
        help="Temperature for response (range: 0.0 to 1.0)",
    )
    parser.add_argument(
        "-m",
        "--mode",
        type=int,
        default=1,
        help="Mode selection:\n" "  1 for chat\n" "  2 for programming assist\n",
    )
    parser.add_argument(
        "-v",
        "--verbosity",
        type=int,
        default=2,
        help="Logging verbosity:\n"
        "  1 for DEBUG\n"
        "  2 for INFO\n"
        "  3 for WARNING\n"
        "  4 for ERROR\n"
        "  5 for CRITICAL\n",
    )
    parser.add_argument(
        "-TT", "--top_p", type=float, default=1.0, help="Top-p sampling for response"
    )
    parser.add_argument(
        "-n",
        "--num-suggestions",
        type=int,
        default=5,
        help="Number of suggestions to generate in programming assist mode\n",
    )
    args = parser.parse_args()

    # Set up logging
    logging.basicConfig(
        level=[
            None,
            logging.DEBUG,
            logging.INFO,
            logging.WARNING,
            logging.ERROR,
            logging.CRITICAL,
        ][args.verbosity]
    )
    logger = logging.getLogger()

    banner_color = "bold green"

    return args, parser, ENGINE_DESCRIPTIONS, banner_color, logger


def display_ascii_art():
    with open("resources/ascii.txt", "r", encoding="utf-8") as f:
        ascii_art = f.read()
    with console.status("[bold green]Loading...") as status:
        console.print(Text(ascii_art, style="bold red"))


def display_random_quote_or_haiku():
    selected_list = random.choice([haikus, hacking_quotes])
    display_text = random.choice(selected_list)
    console.print(
        Text(
            "═════════════════════════════════════════════════════\n",
            style=f"{banner_color}",
        )
    )
    console.print(Text(display_text, style=f"italic {banner_color}"))


def display_random_quote_or_haiku():
    selected_list = random.choice([haikus, hacking_quotes])
    display_text = random.choice(selected_list)
    with console.status("[bold green]Loading...") as status:
        console.print(Text(display_text, style=f"italic {banner_color}"))


def valid_integer(
    prompt, error_message="Invalid input. Please enter a valid number.\n"
):
    while True:
        try:
            value = int(input(prompt))
            break
        except ValueError:
            print(error_message)
    return value


def valid_float(prompt, error_message="Invalid input. Please enter a valid number.\n"):
    while True:
        try:
            value = float(input(prompt))
            break
        except ValueError:
            print(error_message)
    return value


def exit_convo():
    console.print("\n[bold red]Exiting conversation mode...[/]")
    time.sleep(1)


def exit_program():
    console.print("\n[bold red]Exiting sentAI ChatGPT...[/]")
    time.sleep(1)
    exit()


def chatgpt_response(prompt):
    """
    Send a prompt to the ChatGPT API and return the generated response.

    Args:
        prompt (str): The input prompt for the ChatGPT API.

    Returns:
        str: The generated text from the ChatGPT API.
    """
    logger.debug("Sending prompt to OpenAI API")
    console.print(
        Text(
            "\n═════════════════════════════════════════════════════",
            style=f"{banner_color}",
        )
    )
    console.print("Sending user input to ChatGPT...", style=f"bold yellow")

    # Measure the time it takes to get a response
    start_time = time.perf_counter()

    try:
        response = openai.Completion.create(
            engine=args.engine,
            prompt="\n".join(history + [prompt]),
            max_tokens=args.max_tokens,
            n=1,
            stop=None,
            temperature=args.temperature,
            top_p=args.top_p,
        )
    except openai.error.OpenAIError as e:
        logger.error(f"API error: {e}")
        return "Error: Unable to get a response from ChatGPT."

    end_time = time.perf_counter()
    response_time = end_time - start_time

    generated_text = response.choices[0].text.strip()
    logger.debug(f"Received response: {generated_text}")
    history.append(prompt)
    history.append(generated_text)

    # Print the response time in yellow
    console.print(
        Text(
            "═════════════════════════════════════════════════════",
            style=f"{banner_color}",
        )
    )
    console.print(
        Text(f"Response time: {response_time:.2f} seconds", style="bold yellow")
    )

    return generated_text


def chat_mode():
    """
    Chat mode: Allows the user to have a conversation with the ChatGPT model.
    """
    # function body
    console.print(
        Text(
            "\n═════════════════════════════════════════════════════",
            style=f"{banner_color}",
        )
    )
    console.print("[bold green]Mode: Chat[/]")
    console.print(
        Text(
            "═════════════════════════════════════════════════════",
            style=f"{banner_color}",
        )
    )
    console.print("[bold blue]Type 'EXIT@@' to kill programa at anytime![/]")
    console.print(
        Text(
            "═════════════════════════════════════════════════════\n",
            style=f"{banner_color}",
        )
    )

    while True:
        console.print(Text("User Prompt:", style="red"), "\n -> ", end="")
        user_input = input()

        if user_input.strip().upper() == "EXIT@@":
            exit_convo()
            break
        generated_text = chatgpt_response(user_input)
        console.print(
            Text(
                "═════════════════════════════════════════════════════\n",
                style=f"{banner_color}",
            )
        )
        console.print(Text("ChatGPT:", style="bold green"), "\n -> ", end="")
        console.print(Text(generated_text, style=f"bold blue"))
        console.print(
            Text(
                "\n═════════════════════════════════════════════════════\n",
                style=f"{banner_color}",
            )
        )


def programming_assist_mode():
    iterations = valid_integer("\nHow many lines of code do you want to generate? ")

    for i in range(iterations):
        console.print(f"\n[bold cyan]Code Line {i + 1} Prompt:[/] ", end="")
        prompt = input()
        generated_text = chatgpt_response(prompt)
        console.print(f"[bold yellow]Generated Code Line {i + 1}:[/] {generated_text}")


if __name__ == "__main__":
    display_ascii_art()

    (
        args,
        parser,
        ENGINE_DESCRIPTIONS,
        banner_color,
        logger,
    ) = setup_arguments_and_logging()

    display_random_quote_or_haiku()

    if args.interactive:
        console.print(
            Text(
                "\n═════════════════════════════════════════════════════",
                style=f"{banner_color}",
            )
        )
        console.print("[bold green]Interactive Mode[/]")
        console.print(
            Text(
                "═════════════════════════════════════════════════════\n",
                style=f"{banner_color}",
            )
        )
        while True:
            args.mode = valid_integer(
                "Select mode (1 for chat, 2 for programming assist): ",
                "Invalid input. Please enter 1 or 2.",
            )
            if args.mode in (1, 2):
                break
            print(
                "Invalid mode. Please choose either 1 for chat or 2 for programming assist."
            )

    if args.mode == 1:
        chat_mode()
    elif args.mode == 2:
        console.print("\n[bold green]Mode: Programming Assist[/]")
        programming_assist_mode()

    exit_program()
