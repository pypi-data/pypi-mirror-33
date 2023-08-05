from pyDatalog import pyDatalog

# Class that define a relation in the knowledge database
class Relation(pyDatalog.Mixin):

    def __init__(self, child_lang, child, relation, parent_lang, parent):
        # call the initialization method of the Mixin class
        super(Relation, self).__init__()
        self.child_lang = child_lang
        self.child = child
        self.relation = relation
        self.parent_lang = parent_lang
        self.parent = parent

    def __repr__(self):  # specifies how to display a Relation
        return self.child_lang+":"+self.child+" "+self.relation+" "+self.parent_lang+":"+self.parent
