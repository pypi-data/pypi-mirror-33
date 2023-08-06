import os
import re
import shutil
import subprocess
import pkg_resources
import pandas
# import toytree
# import toyplot
import phylovega
import phylopandas
import pyasr
import dendropy
from functools import wraps
from time import localtime, strftime

import Bio.Phylo.Applications

def track_in_history(method):
    """Track this call in the history DataFrame"""
    @wraps(method)
    def wrapper(self, *args, **kwargs):
        """"""
        # Now run method
        output = method(self, *args, **kwargs)

        # Store method in history.
        # Prepare data for history dataframe
        time =strftime("%Y-%m-%d %H:%M:%S", localtime())
        args_as_str = ",".join([str(a) for a in args])
        kwargs_as_str = ",".join([str((key, val)) for key, val in kwargs.items()])

        # Create row
        history = pandas.DataFrame({'time':[time],
            'method':[method.__name__],
            'args':[args_as_str],
            'kwargs':[kwargs_as_str]}, dtype=str)

        # Append to main history dataframe
        self.history = self.history.append(history, ignore_index=True)

        # Write history to file.
        history_file = os.path.join(self.project_dir, 'history.csv')
        self.history.to_csv(history_file)
        self.save()
        return output
    return wrapper

class PhylogeneticsProject(object):
    """A lightweight python object that manages phylogenetic data.

    There are three datatypes stored in a PhylogeneticsProject object:

        * 'tips' : A DataFrame with an alignment and information about the tips of the tree.
        * 'ancs' : A DataFrame with information about the ancestors of the tree.
        * 'tree' : A dendropy.Tree object containing the topology of the phylogenetic tree.

    Parameters
    ----------
    project_dir : str
        the directory to store the phylogenetic data.

    overwrite : bool (default: False)
        allow overwriting a project that already exists in project_dir location.
    """
    def __init__(self, project_dir, overwrite=False):
        # Get current time for history.
        time = strftime("%Y-%m-%d %H:%M:%S", localtime())

        # Set up a project directory
        if os.path.exists(project_dir) and overwrite is False:
            raise Exception("Project already exists! Use `PhylogeneticsProject.load` or delete the project.")
        elif not os.path.exists(project_dir):
            os.makedirs(project_dir)

        self.project_dir = project_dir

        # DataFrame for storing data.
        self.data = {'tips':None, 'ancs':None, 'tree':None}

        # Create a history database.
        self.history = pandas.DataFrame({'time':[time],
            'method':['__init__'],
            'args':[project_dir],
            'kwargs':[None]}, dtype=str)

        # Write history to file.
        history_file = os.path.join(self.project_dir, 'history.csv')
        self.history.to_csv(history_file)

    def __str__(self):
        # Get history
        history = self.history.iloc[-1]
        tips_bool = self.data['tips'] is not None
        ancs_bool = self.data['ancs'] is not None
        tree_bool = self.data['tree'] is not None

        # Start building history.
        info = ["PhylogeneticsProject(project_dir={})\n".format(self.project_dir),
                "    last modified\t{}\n".format(history['time']),
                "    last edit\t\t{}\n".format(history['method'])]

        # If leafs, add stats
        info += ["    tips\t\t{}\n".format(tips_bool)]
        if tips_bool:
            leafs = self.data['tips']
            info += ["        - num of tips\t{}\n".format(len(leafs))]

        # If ancestors, add stats.
        info += ["    ancs\t\t{}\n".format(ancs_bool)]
        if ancs_bool:
            ancs = self.data['ancs']
            info += ["        - num of ancs\t{}\n".format(len(ancs))]

        # If tree, add stats.
        info += ["    tree\t\t{}\n".format(tree_bool)]
        return "".join(info).strip()

    def __repr__(self):
        return self.__str__()

    def save(self):
        """Save this project to file."""
        # Save history
        history_path = os.path.join(self.project_dir, 'history.csv')
        self.history.to_csv(history_path)

        # Save tips data.
        if self.data['tips'] is not None:
            tips_path = os.path.join(self.project_dir, 'tips.csv')
            self.data['tips'].to_csv(tips_path)

        # Save ancs data.
        if self.data['ancs'] is not None:
            ancs_path = os.path.join(self.project_dir, 'ancs.csv')
            self.data['ancs'].to_csv(ancs_path)

        # Save tree data.
        if self.data['tree'] is not None:
            tree_path = os.path.join(self.project_dir, 'tree.newick')
            self.data['tree'].write(path=tree_path, schema='newick')
        return self

    @classmethod
    def load(cls, project_dir):
        """Load a project from a project directory."""
        if not os.path.exists(project_dir):
            raise Exception("project_dir does not exist")

        # load history
        history_path = os.path.join(project_dir, 'history.csv')
        history = pandas.read_csv(history_path, index_col=0)

        # Initialize a TreeProject class.
        self = cls(project_dir, overwrite=True)

        # Append old history.
        self.history = history

        # Try reading tips
        try:
            tips_path = os.path.join(self.project_dir, 'tips.csv')
            tips_df = pandas.read_csv(tips_path, index_col=0)
            self._add_tips(tips_df)
        except: pass

        # Try reading ancestors
        try:
            ancs_path = os.path.join(self.project_dir, 'ancs.csv')
            ancs_df = pandas.read_csv(ancs_path, index_col=0)
            self._add_ancs(ancs_df)
        except: pass

        # Try reading tree
        try:
            tree_path = os.path.join(self.project_dir, 'tree.newick')
            tree = dendropy.Tree.get(path=tree_path, schema='newick')
            self._add_tree(tree)
        except: pass

        return self

    def _add_tips(self, data):
        """Add data about the tips (must be a DataFrame) to the project class."""
        if isinstance(data, pandas.DataFrame) is False:
            raise Exception('Bad datatype.')

        # Add unique ids
        if 'unique_id' not in data:
            unique_ids = ["tip{:07d}".format(i) for i in range(len(data))]
            col = pandas.Series(unique_ids, index=data.index)
            data['unique_id'] = col

        self.data['tips'] = data
        self.tips = data

    def _add_ancs(self, data):
        """Add data about the ancestors (must be a DataFrame) to the project class."""
        if isinstance(data, pandas.DataFrame) is False:
            raise Exception('Bad datatype.')

        # Add unique ids
        if 'unique_id' not in data:
            unique_ids = ["anc{:07d}".format(i) for i in range(len(data))]
            col = pandas.Series(unique_ids, index=data.index)
            data['unique_id'] = col

        self.data['ancs'] = data
        self.ancestors = data

    def _add_tree(self, data):
        """Add tree object (must be dendropy.Tree object) to the project class."""
        if isinstance(data, dendropy.Tree) == False:
            raise Exception('Bad datatype.')
        self.data['tree'] = data
        self.tree = data

    @track_in_history
    def add_data(self, dtype, data):
        """Add data to this phylogenetic project.

        Three types of data can be passed to this object.
            'tips' : A DataFrame with an alignment and information about the tips of
                    the tree.
            'ancs' : A DataFrame with information about the ancestors of the tree.
            'tree' : A dendropy.Tree object containing the topology of the phylogenetic tree.

        Parameters
        ----------
        dtype : str
            the type of data you are giving the project: 'tips', 'ancs', or 'tree'.

        data :
            the data to store.
        """
        if dtype not in ['tips', 'ancs', 'tree']:
            raise Exception('dtype is not valid.')

        # Call method on data.
        method = getattr(self, '_add_{}'.format(dtype))
        method(data)
        return self

    @track_in_history
    def read_data(self, dtype, path, schema='fasta', **kwargs):
        """Read data from file.

        Three types of data can be passed to this object.
            'tips' : A DataFrame with an alignment and information about the tips of
                    the tree.
            'ancs' : A DataFrame with information about the ancestors of the tree.
            'tree' : A dendropy.Tree object containing the topology of the phylogenetic tree.

        Parameters
        ----------
        dtype : str
            the type of data you are giving the project: 'tips', 'ancs', or 'tree'.

        path : str
            file path to the data.

        schema : str
            the format of the datafile. Must be one of the formats supported by
            PhyloPandas.
        """
        try:
            method_read = getattr(phylopandas, 'read_{}'.format(schema))
        except AttributeError:
            method_read = getattr(pandas, 'read_{}'.format(schema))

        df = method_read(path, **kwargs)
        method_add = getattr(self, '_add_{}'.format(dtype))
        method_add(df)
        return self

    def write_data(self, dtype, path, schema='fasta', **kwargs):
        """Write a piece of the project data to file.

        Parameters
        ----------
        dtype : str
            the type of data you are giving the project: 'tips', 'ancs', or 'tree'.

        path : str
            file path to the data.

        schema : str
            the format of the datafile. Must be one of the formats supported by
            PhyloPandas.
        """
        df = self.data[dtype]

        # Get write method.
        try:
            method_write = getattr(df, 'to_{}'.format(schema))
        except AttributeError:
            method_write = getattr(df.phylo, 'to_{}'.format(schema))

        method_write(filename=path)
        return self

    @track_in_history
    def compute_tree(self, id_col='unique_id', sequence_col='sequence',
        datatype='aa',
        bootstrap='-1',
        model='LG',
        frequencies='e',
        **kwargs):
        """Use PhyML to build a phylogenetic tree.

        Parameters
        ----------
        id_col : str (default: 'unique_id')
            column in `tips` DataFrame to use as the labels in the tree. Don't change
            this unless you know what you are doing.

        sequence_col : str (default: 'sequence')
            Column in the `tips` DataFrame that contains the alignment sequences
            for constructing the phylogenetic tree.

        bootstrap : str (default : -1 [aLRT values])
            Bootstrap values to use as support for the nodes of the tree. See PhyML's
            docs for more information. The default is to calculate aLRT supports.

        model : str (default : 'lg')
            the evolutionary transition matrix to use to model substitutions.

        frequencies :  str (default : 'e')
            Nucleotide or amino-acid frequencies.

        Note
        ----
        keyword arguments from what is mentioned above are translated to
        commandline arguments for PhyML. Read PhyML's docs to see a list of all
        arguments that can passed to PhyML.
        """
        df = self.data['tips']

        # Write file to disk
        fasta_file = os.path.join(self.project_dir, 'alignment.phy')
        fasta_data = df.phylo.to_fasta_twoline(sequence_col=sequence_col, id_col=id_col, id_only=True)
        fasta_data = "{} {}\n{}".format(len(df), len(df.sequence[0]), fasta_data)
        with open(fasta_file, 'w') as f: f.write(fasta_data)

        # Prepare options
        options = {
            'input':fasta_file,
            'datatype':datatype,
            'bootstrap':bootstrap,
            'model':model,
            'frequencies':frequencies,
        }
        # Update with any kwargs manually set by users.
        options.update(**kwargs)

        # Build command line arguments for PhyML.
        cml = Bio.Phylo.Applications.PhymlCommandline(**options)
        cml_args = str(cml).split()
        output = subprocess.run(cml_args)

        # # Get path (catch variations in file extension generated by phyml)
        try:
            tree_file = os.path.join(self.project_dir, 'alignment.phy_phyml_tree')
            tree = dendropy.Tree.get(path=tree_file, schema='newick')

        except FileNotFoundError:
            tree_file = os.path.join(self.project_dir, 'alignment.phy_phyml_tree.txt')
            tree = dendropy.Tree.get(path=tree_file, schema='newick')

        self._add_tree(tree)
        return self

    @track_in_history
    def compute_reconstruction(self, id_col='unique_id', sequence_col='sequence', **kwargs):
        """Use PAML (via PyASR) to build a phylogenetic tree.

        Parameters
        ----------
        id_col : str (default: 'unique_id')
            column in `tips` DataFrame to use as the labels in the tree. Don't change
            this unless you know what you are doing.

        sequence_col : str (default: 'sequence')
            Column in the `tips` DataFrame that contains the alignment sequences
            for constructing the phylogenetic tree.

        Note
        ----
        Keyword arguments from what is mentioned above are translated to
        commandline arguments for PAML. Read PAML's docs to see a list of all
        arguments that can passed to PAML.
        """
        df_seqs = self.data['tips']
        tree = self.data['tree']

        ###### BIT OF A HACK  ########################

        # Parse PhyML stats for alpha (catch variations in phyml output file extensions)
        data = {}
        try:
            phyml_file = os.path.join(self.project_dir, 'alignment.phy_phyml_stats')

            with open(phyml_file, 'r') as f:
                data_string = f.read()

        except FileNotFoundError:
            phyml_file = os.path.join(self.project_dir, 'alignment.phy_phyml_stats.txt')

            with open(phyml_file, 'r') as f:
                data_string = f.read()

        option_regex = re.compile("\.[\w\t ]+:.+\n|\- [\w\t ]+:.+\n")
        for pair in option_regex.findall(data_string):
            # Split the pair
            parse = pair.split(":")
            # Each pair has either a `. ` or `- ` in front. Remove those
            key = parse[0][2:]
            # Remove whitespace
            value = parse[1].lstrip().rstrip()
            # add to data dict
            data[key] = value

        # Get alpha
        alpha = data['Gamma shape parameter']
        alpha = alpha[:5]

        ###### END HACK #################################

        # Write file to disk
        df_seqs, df_ancs, tree_ancs = pyasr.reconstruct(df_seqs, tree,
            working_dir=self.project_dir,
            id_col=id_col, sequence_col=sequence_col,
            alpha=alpha,
            save_ancestors=True,
            **kwargs)

        # Add data to TreeProject.
        self._add_ancs(df_ancs)
        self._add_tree(tree_ancs)
        return self

    def show(self):
        """Show rough interactive tree.
        """
        # Write a dummy tree
        tree_path = os.path.join(self.project_dir, 'vega-tree.newick')
        self.data['tree'].write(path=tree_path, schema='newick')
        tree_df = phylopandas.read_newick(tree_path)

        # Create vega tree
        vegatree = phylovega.VegaTree(tree_df)

        # Write vega tree.
        vega_path = os.path.join(self.project_dir, 'vega-tree.vg.json')
        vegatree.to_json(vega_path)

        # Display vega tree
        vegatree.display()

    def decorate_tree(self, tips_attrs, anc_attrs):
        """Map taxon attributes from dataframe to a dendropy tree.
        """
        ###### Map Taxon info to tree
        # Iterate over index
        for uid in self.tips['unique_id']:
            # Get row
            row = self.tips[self.tips['unique_id'] == uid]

            # Get node in tree
            node = self.tree.find_node_with_taxon_label(uid)

            # Set attributes
            for label in tips_attrs:
                # add to annotations
                value = row[label].values[0]
                node.taxon.annotations.add_new(label, value)

        # Map ancestors if info is given
        for uid in self.ancestors['id']:
            # Get row
            row = self.ancestors[self.ancestors['id'] == uid]

            # Get node in tree
            node = self.tree.find_node_with_label(str(uid))

            # Set attributes
            if node is not None:
                for label in anc_attrs:
                    # add to annotations
                    value = row[label].values[0]
                    node.annotations.add_new(label, value)
