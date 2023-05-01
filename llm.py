#!/usr/bin/env python
### Examples
# llm.py prompt.txt
# llm.py prompt_template.txt argument1 argument2
# echo "Just say hello" | llm.py
# echo "input text" | llm.py prompt_template.txt
# llm.py --stream "Just say hello in {{language}}" Japanese

import click
import os
import sys
import openai
import re
import jinja2
import logging

file_path_regex = r'^(?:\.{0,2}[\\/])?([^\/\:\*\?\<\>\|]+[\\/])*([^\/\:\*\?\<\>\|]+\.\w+)$'
def is_file_path(s):
    return bool(re.match(file_path_regex, s))

def is_prompt_template(prompt):
  # if prompt contains {{...}} then it is a prompt template
  return bool(re.search(r'\{\{.*\}\}', prompt))

def extract_variable_names_from_prompt_template(prompt_template):
  return re.findall(r'\{\{(.*)\}\}', prompt_template)

def render_prompt_template(prompt_template, args):
  template = jinja2.Template(prompt_template)
  variable_names = extract_variable_names_from_prompt_template(prompt_template)

  template_args = {}
  for i, variable_name in enumerate(variable_names):
    template_args[variable_name] = args[i]

  return template.render(template_args)

@click.command()
@click.argument('prompt', required=False)
@click.argument('args', nargs=-1)
@click.option("-s", "--stream", is_flag=True, help="Stream output")
@click.option("-v", "--verbose", is_flag=True, help="Verbose output")
def cli(prompt, args, stream, verbose):
    openai.api_key = get_openai_api_key()
    model = "gpt-3.5-turbo"

    if verbose:
      logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

    if prompt:
      is_file_prompt = os.path.isfile(prompt)
      if is_file_prompt:
        file_path = prompt
        prompt = open(file_path, 'r').read()
      else:
        if is_file_path(prompt):
          file_path = prompt
          print("Error: File does not exist: {}".format(file_path), file=sys.stderr)
          sys.exit(1)

      if is_prompt_template(prompt):
        prompt_template = prompt
        variable_names = extract_variable_names_from_prompt_template(prompt_template)

        if len(args) == 0 and len(variable_names) == 1:
          arg = sys.stdin.read()
          args = (arg,)

        if len(variable_names) != len(args):
          print("Error: Number of arguments does not match number of variables in prompt template: {}".format(variable_names), file=sys.stderr)
          sys.exit(1)

        expanded_args = []
        for arg in args:
          is_file = os.path.isfile(arg)
          if is_file:
            arg = open(file_path, 'r').read()
          elif arg == "-":
            arg = sys.stdin.read()

          expanded_args.append(arg)

        prompt = render_prompt_template(prompt_template, expanded_args)

      logging.debug(prompt)

    else:
       # read prompt from stdin
       prompt = sys.stdin.read()

    messages = []
    messages.append({"role": "user", "content": prompt})

    if stream:
        response = []
        for chunk in openai.ChatCompletion.create(
            model=model,
            messages=messages,
            stream=True,
        ):
            content = chunk["choices"][0].get("delta", {}).get("content")
            if content is not None:
                response.append(content)
                print(content, end="")
                sys.stdout.flush()
        print("")
    else:
        response = openai.ChatCompletion.create(
            model=model,
            messages=messages,
        )
        content = response.choices[0].message.content
        print(content)

def get_openai_api_key():
    # Expand this to home directory / ~.openai-api-key.txt
    if "OPENAI_API_KEY" in os.environ:
        return os.environ["OPENAI_API_KEY"]
    path = os.path.expanduser("~/.openai-api-key.txt")
    # If the file exists, read it
    if os.path.exists(path):
        with open(path) as fp:
            return fp.read().strip()
    raise click.ClickException(
        "No OpenAI API key found. Set OPENAI_API_KEY environment variable or create ~/.openai-api-key.txt"
    )

if __name__ == '__main__':
    cli()

