#!/usr/bin/env python
# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4

import cmd
import readline
import sys
import traceback
import types
from src.console_controller import ConsoleController

def try_catch(command, args=None):
    try:
        if args is not None:
            return command(*args)
        else:
            return command()
    except:
        print("Sorry, that command raised an exception. Here's what I know:\n")
        print(traceback.format_exc())

###################################################################################################        
## Begin obscure bull@#$% code
###################################################################################################

# Generic filter arg selector command console
class FilterArgCmd(cmd.Cmd):

    def __init__(self, prompt_prefix, controller, context, line, filter_name):
        cmd.Cmd.__init__(self)
        
        # TODO
        self.helptext = "This is the FILTER "+filter_name+" "+" console. Here you select which filter\n" \
                        "argument you want to view or modify. These are the filter arguments:\n\n"
        self.helptext += ', '.join(controller.filter_mgr.filter_args[filter_name])
        
        self.prompt = prompt_prefix[:-2] + ' ' + filter_name +'> '
        self.controller = controller
        self.context = context
        self.filter_name = filter_name
        if line:
            self.cmdqueue = [line] # Execute default method with path as arg
        else:
            print(self.helptext)
        readline.set_history_length(1000)
        try:
            readline.read_history_file('.gaghistory')
        except IOError:
            sys.stderr.write("No .gaghistory file available...\n")
            
        # Set up filter arg do functions
        for arg in controller.filter_mgr.filter_args[self.filter_name]:
            # First real closure #teddy'sallgrownup
            # traps arg variable
            def do_arg(self, line, filter_arg = arg):
                filtercmd = FilterArgSetGetCmd(self.prompt, self.controller, self.context, line, self.filter_name, filter_arg)
                filtercmd.cmdloop()
                if self.context["go_home"]:
                    return True
            setattr(self, 'do_'+arg, types.MethodType(do_arg, self))

    def precmd(self, line):
        readline.write_history_file('.gaghistory')
        return cmd.Cmd.precmd(self, line)

    def help_home(self):
        print("\nExit this console and return to the main GAG console.\n")

    def do_home(self, line):
        self.context['go_home'] = True
        return True

    def emptyline(self):
        print(self.helptext)

    def default(self, line):
        print("No such "+self.filter_name+" argument: "+line+"\n");
        


# Generic filter arg setter/getter command console
class FilterArgSetGetCmd(cmd.Cmd):

    def __init__(self, prompt_prefix, controller, context, line, filter_name, arg_name):
        cmd.Cmd.__init__(self)
        
        self.helptext = "This is the FILTER "+filter_name+" "+arg_name+" console. Type a value\n" \
                        "to set the filter argument value, or simply press enter to see the current\n" \
                        "value.\n"
        
        self.prompt = prompt_prefix[:-2] + ' ' + arg_name +'> '
        self.controller = controller
        self.context = context
        self.filter_name = filter_name
        self.arg_name = arg_name
        if line:
            context['go_home'] = True
            self.cmdqueue = [line] # Execute default method with path as arg
        else:
            print(self.helptext)
        readline.set_history_length(1000)
        try:
            readline.read_history_file('.gaghistory')
        except IOError:
            sys.stderr.write("No .gaghistory file available...\n")

    def precmd(self, line):
        readline.write_history_file('.gaghistory')
        return cmd.Cmd.precmd(self, line)

    def help_home(self):
        print("\nExit this console and return to the main GAG console.\n")

    def do_home(self, line):
        self.context['go_home'] = True
        return True

    def emptyline(self):
        print(self.filter_name+" "+self.arg_name+": "+str(try_catch(self.controller.filter_mgr.get_filter_arg, [self.filter_name, self.arg_name]))+"\n\n")

    def default(self, line):
        line = line.strip()
        if line:
            try_catch(self.controller.filter_mgr.set_filter_arg, [self.filter_name, self.arg_name, line])
            print(self.filter_name+" "+self.arg_name+" set to "+line+'\n')
            return True



###################################################################################################
## End obscure bull@#$% code, begin sanity
###################################################################################################

class GagCmd(cmd.Cmd):

## Setup, loading and saving sessions, exit, etc.

    intro = "                                                                                \n                                        ,,                                      \n              ~++=:,                  =OMNZ:                  :=?77I=,          \n           :7DMMMMMMD7:              ~DMMMMZ               =$DMMMMMMMM8+        \n         :7NMMMMMMMMMMN7,            $MMMMMN=            ~ZMMMMMMMMMMMMZ,       \n        ?NMMMNZ+~+IONMMN?           INMMNMMMI           INMMMDZ?~,,:+I?:        \n       +NMMN7:      :?$I:          INMMNZMMMZ         :$MMMD?                   \n      :8MMM?                      7MMMD+=NMM8,       :OMMMO~                    \n      7MMMZ,                     7MMMD= ,8MMM?       ZMMMZ,                     \n     :8MMN+                    ,$MMMN+   IMMMO      ~NMMD~     ,+$ZI+==~,       \n     ~DMMD~    ~7OZ$Z8NNZ:    +DMMMD$I?~:~DMMN+     +NMM8      IMMMMMMMMO:      \n      $MMM8:   ,OMMMMMMMN=   INMMN$$MMMMMMMMMMZ     ~DMMMI     ~8MMMMMMMZ:      \n      ,ZMMMD?,   ?NMMMNZ~   INMMD+ =ONMMMMMMMMN~     +DMMM$:     ,=$MMMD:       \n       ,$MMMMM87+IONMMMI   ?NMMN=     :=+??OMMM$      =8MMMM87=, ,+8MMMZ        \n         +8MMMMMMMMMMMO~  ~D0GE?           =NMM$       :$NMMMMMMNMMMMMO:        \n           :I8NMMMMNO+,   :OMD?             +Z7~         :I8NMMMMMMMDI,         \n               :~~:        ,,,                               ~?7$7?~            \n                                                                                \n                                                                                "+\
    "\nWelcome to the GAG console!\n"+\
    "Type 'help' for available commands.\n"

    no_genome_message = "\nIt looks like no genome is currently loaded. Try the 'load' command.\n"+\
            "Type 'help load' to learn how to use it, or just 'help' for general advice.\n"

    def __init__(self):
        cmd.Cmd.__init__(self)
        self.prompt = "GAG> "
        readline.set_history_length(1000)
        try:
            readline.read_history_file('.gaghistory')
        except IOError:
            sys.stderr.write("No .gaghistory file available...\n")
        self.controller = ConsoleController() 

    def precmd(self, line):
        readline.write_history_file('.gaghistory')
        return cmd.Cmd.precmd(self, line)

    def help_load(self):
        print("\nThis command takes you the GAG LOAD menu. There you can specify the location of")
        print("your files and load them into memory.")
        print("Alternately, just type 'load <path>' and avoid the submenu altogether.\n")

    def do_load(self, line):
        path_to_load = line.strip()
        loadcmd = LoadCmd(self.prompt, self.controller, path_to_load)
        loadcmd.cmdloop()

    def help_filter(self):
        print("\nThis command takes you to the GAG FILTER menu. There you can apply filters to the genome")
        print("to filter out suspicious data. Alternately, just type:\n")
        print("'filter <name_of_filter> <filter_arg_name> <set or get> [value if setting]'\n")
        print("if you've done this before :)\n")

    def do_filter(self, line):
        if self.controller.genome_is_loaded():
            filtercmd = FilterCmd(self.prompt, self.controller, line)
            filtercmd.cmdloop()
        else:
            print(self.no_genome_message)
            
    def help_fix(self):
        print("\nThis command takes you to the GAG FIX menu. There you can apply fixes to the genome,")
        print("to resolve issues such as terminal Ns, invalid start and stop codons, etc.")
        print("Fixes are applied when you type the 'info' command or when you write")
        print("the genome to a file.")
        print("Alternately, just type 'fix <name_of_fix> if you've done this before :)\n")

    def do_fix(self, line):
        if self.controller.genome_is_loaded():
            name_of_fix = line.strip()
            fixcmd = FixCmd(self.prompt, self.controller, name_of_fix)
            fixcmd.cmdloop()
        else:
            print(self.no_genome_message)

    def help_write(self):
        print("\nThis command takes you to the GAG WRITE menu. There you can write genomic data")
        print("to the screen or to a file. You can write at the CDS, mRNA, gene, sequence or genome level.")
        print("Available formats: fasta, gff, tbl.\n")
        
    def do_write(self, line):
        if self.controller.genome_is_loaded():
            writecmd = WriteCmd(self.prompt, self.controller, line) # Pass args to next console for parsing
            writecmd.cmdloop()
        else:
            print(self.no_genome_message)

    def help_exit(self):
        print("\nExit this console.\n")

    def do_exit(self, line):
        return True
        
    def help_info(self):
        print("\nPrints summary statistics about original genome (from file)" +\
                " and modified genome (filters and fixes applied).")
        print("May take a moment to run.\n")

    def do_info(self, line):
        if self.controller.genome_is_loaded():
            print(try_catch(self.controller.stats, None))
        else:
            print(self.no_genome_message)


##############################################

class FilterCmd(cmd.Cmd):

    helptext = "\nThis is the GAG FILTER menu.\n"+\
            "You can inspect and modify the following filters: "+\
            "cds_length, exon_length, intron_length, gene_length.\n"+\
            "(You can type 'home' at any time to return to the main GAG console.)\n"+\
            "Type the name of a filter to inspect or modify it.\n"

    def __init__(self, prompt_prefix, controller, line):
        cmd.Cmd.__init__(self)
        self.prompt = prompt_prefix[:-2] + " FILTER> "
        self.controller = controller
        self.context = {"go_home": False}
        if line:
            self.cmdqueue = [line] # Execute default method with path as arg
        else:
            print(self.helptext)
        readline.set_history_length(1000)
        try:
            readline.read_history_file('.gaghistory')
        except IOError:
            sys.stderr.write("No .gaghistory file available...\n")

    def precmd(self, line):
        readline.write_history_file('.gaghistory')
        return cmd.Cmd.precmd(self, line)

    def help_home(self):
        print("\nExit this console and return to the main GAG console.\n")

    def do_home(self, line):
        return True

    def help_cds_length(self):
        print("\nYou can filter by min or max CDS length. mRNAs who's CDSs don't make the cut are removed.\n")
        
    def do_cds_length(self, line):
        cdscmd = FilterArgCmd(self.prompt, self.controller, self.context, line, 'cds_length')
        cdscmd.cmdloop()
        if self.context["go_home"]:
            return True

    def emptyline(self):
        print(self.helptext)

    def default(self, line):
        print("Sorry, can't filter " + line)
        print(self.helptext)

##############################################

class FixCmd(cmd.Cmd):

    helptext = "\nThis is the GAG FIX menu.\n"+\
            "You can apply the following fixes: "+\
            "terminal_ns, start_stop_codons.\n"+\
            "(You can type 'home' at any time to return to the main GAG console.)\n"+\
            "Type the name of a fix to enable it. Type 'all' to enable everything.\n\n"+\
            "terminal_ns, start_stop_codons or all?\n"

    def __init__(self, prompt_prefix, controller, name_of_fix):
        cmd.Cmd.__init__(self)
        self.prompt = prompt_prefix[:-2] + " FIX> "
        self.controller = controller
        if name_of_fix:
            self.cmdqueue = [name_of_fix] # Execute default method with path as arg
        else:
            print(self.helptext)
        readline.set_history_length(1000)
        try:
            readline.read_history_file('.gaghistory')
        except IOError:
            sys.stderr.write("No .gaghistory file available...\n")

    def precmd(self, line):
        readline.write_history_file('.gaghistory')
        return cmd.Cmd.precmd(self, line)

    def help_home(self):
        print("\nExit this console and return to the main GAG console.\n")

    def do_home(self, line):
        return True

    def help_terminal_ns(self):
        print("\nWith this fix enabled, GAG will inspect the beginning and end of each")
        print("sequence for the presence of unknown bases ('N' or 'n'). If found, they")
        print("will be removed. Indices of features on the sequence will be automatically")
        print("adjusted, and any mRNA that extended into the trimmed region will be removed.\n")

    def do_terminal_ns(self, line):
        print("\n" + self.controller.fix_terminal_ns() + "\n")

    def help_start_stop_codons(self):
        print("\nSelecting this fix will cause GAG to inspect the first and last three bases of each CDS")
        print("to determine if it contains a valid start and/or stop codon. Information in the original")
        print("GFF regarding start_codon or stop_codon features is disregarded.\n")

    def do_start_stop_codons(self, line):
        print("\n" + self.controller.fix_start_stop_codons() + "\n")

    def help_all(self):
        print("\nEnables all available fixes.\n")

    def do_all(self, line):
        print("\n" + self.controller.fix_terminal_ns())
        print(self.controller.fix_start_stop_codons() + "\n")
        return True

    def emptyline(self):
        print(self.helptext)

    def default(self, line):
        print("Sorry, can't fix " + line)
        print(self.helptext)

##############################################

class LoadCmd(cmd.Cmd):

    helptext = "\nThis is the GAG LOAD menu.\n"+\
            "Type the path to a folder containing your .fasta and .gff files.\n"+\
            "To use the current directory, just hit enter.\n"+\
            "You can type 'home' at any time to return to the main GAG console.\n"+\
            "You'll be returned automatically once your genome is loaded.\n\n"+\
            "Folder path?\n"

    def __init__(self, prompt_prefix, controller, path_to_load):
        cmd.Cmd.__init__(self)
        self.prompt = prompt_prefix[:-2] + " LOAD> "
        self.controller = controller
        if path_to_load:
            self.cmdqueue = [path_to_load] # Execute default method with path as arg
        else:
            print(self.helptext)
        readline.set_history_length(1000)
        try:
            readline.read_history_file('.gaghistory')
        except IOError:
            sys.stderr.write("No .gaghistory file available...\n")

    def precmd(self, line):
        readline.write_history_file('.gaghistory')
        return cmd.Cmd.precmd(self, line)

    def help_home(self):
        print("\nExit this console and return to the main GAG console.\n")

    def do_home(self, line):
        return True

    def genome_loaded(self):
        return self.controller.genome_is_loaded()

    def help_load(self):
        print(self.helptext)

    def emptyline(self):
        self.default(".")
        return self.genome_loaded()

    def default(self, line):
        if self.controller.seqs:
            print("Clearing genome ...")
            self.controller.clear_seqs()
        try_catch(self.controller.load_folder, [line])
        if self.genome_loaded():
            return True
        else:
            print(self.helptext)

################################################

class WriteCmd(cmd.Cmd):

    helptext = "\nWelcome to the GAG WRITE menu.\n"+\
            "You can write at the cds, gene, seq or genome level. Please type your choice.\n"+\
            "(Type 'home' at any time to return to the main GAG console.)\n\n"+\
            "cds, gene, seq or genome?\n"

    def __init__(self, prompt_prefix, controller, line):
        cmd.Cmd.__init__(self)
        self.prompt = prompt_prefix[:-2] + " WRITE> "
        self.controller = controller
        self.context = {"go_home": False}
        if line:
            self.cmdqueue = [line] # Execute default method with passed-in line
        else:
            print(self.helptext)
        readline.set_history_length(1000)
        try:
            readline.read_history_file('.gaghistory')
        except IOError:
            sys.stderr.write("No .gaghistory file available...\n")

    def precmd(self, line):
        readline.write_history_file('.gaghistory')
        return cmd.Cmd.precmd(self, line)

    def help_home(self):
        print("\nExit this console and return to the main GAG console.\n")

    def do_home(self, line):
        return True

    def help_write(self):
        print(self.helptext)

    def emptyline(self):
        print(self.helptext)

    def do_cds(self, line):
        cdscmd = WriteCDSCmd(self.prompt, self.controller, self.context, line)
        cdscmd.cmdloop()
        if self.context["go_home"]:
            return True

    def do_gene(self, line):
        genecmd = WriteGeneCmd(self.prompt, self.controller, self.context, line)
        genecmd.cmdloop()
        if self.context["go_home"]:
            return True

    def do_seq(self, line):
        seqcmd = WriteSeqCmd(self.prompt, self.controller, self.context, line)
        seqcmd.cmdloop()
        if self.context["go_home"]:
            return True

    def do_genome(self, line):
        genomecmd = WriteGenomeCmd(self.prompt, self.controller, self.context, line)
        genomecmd.cmdloop()
        if self.context["go_home"]:
            return True

    def default(self, line):
        response = "\nSorry, I don't know how to write " + line + "."
        response += "Please choose 'cds', 'gene', 'seq' or 'genome',"
        response += "or type 'home' to return to the main menu.\n"
        print(response)

################################################

class WriteCDSCmd(cmd.Cmd):

    helptext = "\nWelcome to the GAG WRITE CDS menu.\n"+\
            "You can write a CDS to fasta, gff or tbl format.\n"+\
            "(Type 'home' at any time to return to the main GAG console.)\n\n"+\
            "fasta, gff or tbl?\n"

    def __init__(self, prompt_prefix, controller, context, line):
        cmd.Cmd.__init__(self)
        self.prompt = prompt_prefix[:-2] + " CDS> "
        self.controller = controller
        self.context = context
        if line:
            self.cmdqueue = [line] # Execute default method with passed-in line
        else:
            print(self.helptext)
        readline.set_history_length(1000)
        try:
            readline.read_history_file('.gaghistory')
        except IOError:
            sys.stderr.write("No .gaghistory file available...\n")

    def precmd(self, line):
        readline.write_history_file('.gaghistory')
        return cmd.Cmd.precmd(self, line)

    def help_home(self):
        print("\nExit this console and return to the main GAG console.\n")

    def do_home(self, line):
        self.context["go_home"] = True
        return True
    
    def do_fasta(self, line):
        cdsfastacmd = WriteCDSFastaCmd(self.prompt, self.controller, self.context, line)
        cdsfastacmd.cmdloop()
        if self.context["go_home"]:
            return True

    def do_gff(self, line):
        print("CDS to gff coming soon!")

    def do_tbl(self, line):
        print("CDs to tbl coming soon!")
    
    def help_writecds(self):
        print(self.helptext)

    def emptyline(self):
        print(self.helptext)

    def default(self, line):
        print("Sorry, I don't know how to write to " + line + " format.")
        print(self.helptext)

################################################

class WriteCDSFastaCmd(cmd.Cmd):

    helptext = "\nWelcome to the GAG WRITE CDS FASTA menu.\n"+\
            "Please type the mRNA id that corresponds to the CDS you want to write.\n"+\
            "(Type 'home' at any time to return to the main GAG console.)\n\n"+\
            "mRNA id?\n"

    def __init__(self, prompt_prefix, controller, context, line):
        cmd.Cmd.__init__(self)
        self.prompt = prompt_prefix[:-2] + " FASTA> "
        self.controller = controller
        self.context = context
        if line:
            self.cmdqueue = [line] # Execute default method with passed-in line
        else:
            print(self.helptext)
        readline.set_history_length(1000)
        try:
            readline.read_history_file('.gaghistory')
        except IOError:
            sys.stderr.write("No .gaghistory file available...\n")

    def precmd(self, line):
        readline.write_history_file('.gaghistory')
        return cmd.Cmd.precmd(self, line)

    def help_home(self):
        print("\nExit this console and return to the main GAG console.\n")

    def do_home(self, line):
        self.context["go_home"] = True
        return True
    
    def help_writecdsfasta(self):
        print(self.helptext)

    def emptyline(self):
        print(self.helptext)

    def default(self, line):
        mrna_id = line.strip()
        if self.controller.contains_mrna(mrna_id):
            print("\n" + try_catch(self.controller.barf_cds_seq, [line]) + "\n")
            self.context["go_home"] = True
            return True
        else:
            print("\nSorry, couldn't find mRNA id '" + mrna_id + "'.")
            print(self.controller.get_n_mrna_ids(5))

################################################

class WriteGeneCmd(cmd.Cmd):

    helptext = "\nWelcome to the GAG WRITE GENE menu.\n"+\
            "You can write a gene to gff or tbl format.\n"+\
            "(Type 'home' at any time to return to the main GAG console.)\n\n"+\
            "gff or tbl?\n"

    def __init__(self, prompt_prefix, controller, context, line):
        cmd.Cmd.__init__(self)
        self.prompt = prompt_prefix[:-2] + " GENE> "
        self.controller = controller
        self.context = context
        if line:
            self.cmdqueue = [line] # Execute default method with passed-in line
        else:
            print(self.helptext)
        readline.set_history_length(1000)
        try:
            readline.read_history_file('.gaghistory')
        except IOError:
            sys.stderr.write("No .gaghistory file available...\n")

    def precmd(self, line):
        readline.write_history_file('.gaghistory')
        return cmd.Cmd.precmd(self, line)

    def help_home(self):
        print("\nExit this console and return to the main GAG console.\n")

    def do_home(self, line):
        self.context["go_home"] = True
        return True
    
    def do_gff(self, line):
        genegffcmd = WriteGeneGFFCmd(self.prompt, self.controller, self.context, line)
        genegffcmd.cmdloop()
        if self.context["go_home"]:
            return True

    def do_tbl(self, line):
        genetblcmd = WriteGeneTBLCmd(self.prompt, self.controller, self.context, line)
        genetblcmd.cmdloop()
        if self.context["go_home"]:
            return True

    def do_fasta(self, line):
        cdsfastacmd = WriteGeneFastaCmd(self.prompt, self.controller, self.context, line)
        cdsfastacmd.cmdloop()
        if self.context["go_home"]:
            return True

    def help_writegene(self):
        print(self.helptext)

    def emptyline(self):
        print(self.helptext)

    def default(self, line):
        print("Sorry, I don't know how to write to " + line + " format.")
        print(self.helptext)

################################################

class WriteGeneGFFCmd(cmd.Cmd):

    helptext = "\nWelcome to the GAG WRITE GENE GFF menu.\n"+\
            "Please type the gene id that you want to write.\n"+\
            "(Type 'home' at any time to return to the main GAG console.)\n\n"+\
            "gene id?\n"

    def __init__(self, prompt_prefix, controller, context, line):
        cmd.Cmd.__init__(self)
        self.prompt = prompt_prefix[:-2] + " GFF> "
        self.controller = controller
        self.context = context
        if line:
            self.cmdqueue = [line] # Execute default method with passed-in line
        else:
            print(self.helptext)
        readline.set_history_length(1000)
        try:
            readline.read_history_file('.gaghistory')
        except IOError:
            sys.stderr.write("No .gaghistory file available...\n")

    def precmd(self, line):
        readline.write_history_file('.gaghistory')
        return cmd.Cmd.precmd(self, line)

    def help_home(self):
        print("\nExit this console and return to the main GAG console.\n")

    def do_home(self, line):
        self.context["go_home"] = True
        return True
    
    def help_writegenegff(self):
        print(self.helptext)

    def emptyline(self):
        print(self.helptext)

    def default(self, line):
        gene_id = line.strip()
        if self.controller.contains_gene(gene_id):
            print("\n" + try_catch(self.controller.barf_gene_gff, [line]) + "\n")
            self.context["go_home"] = True
            return True
        else:
            print("\nSorry, couldn't find gene id '" + gene_id + "'.")
            print(self.controller.get_n_gene_ids(5))

################################################

class WriteGeneTBLCmd(cmd.Cmd):

    helptext = "\nWelcome to the GAG WRITE GENE TBL menu.\n"+\
            "Please type the gene id that you want to write.\n"+\
            "(Type 'home' at any time to return to the main GAG console.)\n\n"+\
            "gene id?\n"

    def __init__(self, prompt_prefix, controller, context, line):
        cmd.Cmd.__init__(self)
        self.prompt = prompt_prefix[:-2] + " TBL> "
        self.controller = controller
        self.context = context
        if line:
            self.cmdqueue = [line] # Execute default method with passed-in line
        else:
            print(self.helptext)
        readline.set_history_length(1000)
        try:
            readline.read_history_file('.gaghistory')
        except IOError:
            sys.stderr.write("No .gaghistory file available...\n")

    def precmd(self, line):
        readline.write_history_file('.gaghistory')
        return cmd.Cmd.precmd(self, line)

    def help_home(self):
        print("\nExit this console and return to the main GAG console.\n")

    def do_home(self, line):
        self.context["go_home"] = True
        return True
    
    def help_writegenegff(self):
        print(self.helptext)

    def emptyline(self):
        print(self.helptext)

    def default(self, line):
        gene_id = line.strip()
        if self.controller.contains_gene(gene_id):
            print("\n" + try_catch(self.controller.barf_gene_tbl, [line]) + "\n")
            self.context["go_home"] = True
            return True
        else:
            print("\nSorry, couldn't find gene id '" + gene_id + "'.")
            print(self.controller.get_n_gene_ids(5))

################################################

class WriteSeqCmd(cmd.Cmd):

    helptext = "\nWelcome to the GAG WRITE SEQ menu.\n"+\
            "(Type 'home' at any time to return to the main GAG console.)\n"+\
            "Please type the seq id you wish to write. To write a subsequence,\n"+\
            "follow the seq id with the start and stop bases.\n\n"+\
            "seq id [start base] [stop base]?\n"

    def __init__(self, prompt_prefix, controller, context, line):
        cmd.Cmd.__init__(self)
        self.prompt = prompt_prefix[:-2] + " SEQ> "
        self.controller = controller
        self.context = context
        if line:
            self.cmdqueue = [line] # Execute default method with passed-in line
        else:
            print(self.helptext)
        readline.set_history_length(1000)
        try:
            readline.read_history_file('.gaghistory')
        except IOError:
            sys.stderr.write("No .gaghistory file available...\n")

    def precmd(self, line):
        readline.write_history_file('.gaghistory')
        return cmd.Cmd.precmd(self, line)

    def help_home(self):
        print("\nExit this console and return to the main GAG console.\n")

    def do_home(self, line):
        self.context["go_home"] = True
        return True
    
    def help_writeseq(self):
        print(self.helptext)

    def emptyline(self):
        print(self.helptext)

    def default(self, line):
        args = line.split()
        seq_id = args[0]
        if self.controller.contains_seq(seq_id):
            print("\n" + try_catch(self.controller.barf_seq, [line]))
            self.context["go_home"] = True
            return True
        else:
            print("\nSorry, couldn't find seq id '" + seq_id + "'.")
            print(self.controller.get_n_seq_ids(5))
            print("seq id [start base] [stop base]?\n")

################################################

class WriteGenomeCmd(cmd.Cmd):

    helptext = "\nWelcome to the GAG WRITE GENOME menu.\n"+\
            "Please type a name for the folder to contain the files.\n"+\
            "The folder will be created -- in other words, don't give an existing folder.\n"+\
            "(Type 'home' at any time to return to the main GAG console.)\n\n"+\
            "folder name?\n"

    def __init__(self, prompt_prefix, controller, context, line):
        cmd.Cmd.__init__(self)
        self.prompt = prompt_prefix[:-2] + " GENOME> "
        self.controller = controller
        self.context = context
        if line:
            self.cmdqueue = [line] # Execute default method with passed-in line
        else:
            print(self.helptext)
        readline.set_history_length(1000)
        try:
            readline.read_history_file('.gaghistory')
        except IOError:
            sys.stderr.write("No .gaghistory file available...\n")

    def precmd(self, line):
        readline.write_history_file('.gaghistory')
        return cmd.Cmd.precmd(self, line)

    def help_home(self):
        print("\nExit this console and return to the main GAG console.\n")

    def do_home(self, line):
        self.context["go_home"] = True
        return True
    
    def help_writegenome(self):
        print(self.helptext)

    def emptyline(self):
        print(self.helptext)

    def default(self, line):
        if self.controller.can_write_to_path(line):
            print(try_catch(self.controller.barf_folder, [line]))
            self.context["go_home"] = True
            return True
        else:
            print("\nSorry, can't write to " + line + "\n")
            print("folder name?\n")

################################################

if __name__ == '__main__':
    GagCmd().cmdloop()
