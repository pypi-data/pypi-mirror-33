#Typing imports
import typing as typ

#External imports

#Internal Imports
import parser # type: ignore

class CLICommand:
    short_description = "ASE's graphical user interface"
    description = ('ASE-GUI.  See the online manual '
                   '(https://wiki.fysik.dtu.dk/ase/ase/gui/gui.html) '
                   'for more information.')

    @staticmethod
    def add_arguments(parser : 'parser') -> None: # type: ignore
        pass

    @staticmethod
    def run(args):
        from catalog.gui.main import main
        main()
