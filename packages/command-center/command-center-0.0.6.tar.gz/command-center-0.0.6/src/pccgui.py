from subprocess import Popen
from tkinter import Tk, Button
from utils import load_scripts
import click


def print_header(line):
    bars = '\u2550' * (len(line)+2)
    print(''.join(['\u2554', bars, '\u2557']))
    print(' '.join(['\u2551', line, '\u2551']))
    print(''.join(['\u255A', bars, '\u255D']))


def script_wrapper(script_command):
    def execute_script():
        print_header('$ ' + script_command)
        Popen(script_command.split(' '))
    return execute_script


@click.command()
@click.option('--col', default=6, help='How many columns of buttons')
def main(col):
    scripts = load_scripts()
    root = Tk()
    root.title('Python Command Center')
    button_settings = dict(ipadx=5, ipady=5, padx=3, pady=3, sticky='EW')
    for i, key in enumerate(scripts):
        button = Button(root, text=key, command=script_wrapper(scripts[key]))
        button.grid(row=i//col, column=i % col, **button_settings)
    root.mainloop()


if __name__ == '__main__':
    main()
