from sqlalchemy import Column, ForeignKey, Integer, String, create_engine, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from settings import DB, GI_2_TAXID_FILE, NAMES_FILE, NODES_FILE, FLUSH_SIZE
from db_session import Session

Base = declarative_base()

class NodesTree(Base):
    __tablename__ = 'NodesTree'

    taxid = Column(Integer, primary_key=True)
    name = Column(String(200))
    parent = Column(Integer)
    rank = Column(String(20))
    gi2taxid  = relationship('Gi2taxid', backref='node')

class Gi2taxid(Base):
    __tablename__ = 'Gi2taxid'

    gi = Column(Integer, primary_key=True)
    taxid = Column(Integer, ForeignKey('NodesTree.taxid'))


Index("gi_idx_on_gitaxid", Gi2taxid.__table__.c.gi, unique=True)
Index("taxid_idx_on_gitaxid", Gi2taxid.__table__.c.taxid)
Index("taxid_idx_on_nodestree", NodesTree.__table__.c.taxid, unique=True)
Index("name_idx_on_nodestree", NodesTree.__table__.c.name)
Index("parent_idx_on_nodestree", NodesTree.__table__.c.parent)


class UpdateTables(object):
    def __init__(self, create, db=DB, flush_size=FLUSH_SIZE, names_file=NAMES_FILE, nodes_file=NODES_FILE, gi2taxid_file=GI_2_TAXID_FILE):
        self.db = db
        self.names_file = names_file
        self.nodes_file = nodes_file
        self.gi2taxid_file = gi2taxid_file
        self.flush_size = flush_size
        self.create = create

    def import_names_nodes(self, db_session):
        # taxid : Node
        tree = {}
        # process the names.dmp
        for line in open(self.names_file, 'r'):
            fields = line.strip().split("\t")
            notion = fields[6]
            taxid = int(fields[0])
            name = fields[2]
            if notion == "scientific name":
                if taxid not in tree:
                    tree[taxid] = [name, "0", ""]
        # process the nodes.dmp
        for line in open(self.nodes_file, 'r'):
            fields = line.strip().split("\t")
            taxid = int(fields[0])
            parent = int(fields[2])
            rank = fields[4]
            if taxid in tree:
                tree.get(taxid)[1] = parent
                tree.get(taxid)[2] = rank
        index=0
        taxid_records = []
        print "Start update NodesTree table."
        for taxid in tree.keys():
            if self.create or (not self.create and not db_session.query(NodesTree).filter(NodesTree.taxid == taxid).all()):
                index += 1
                taxid_records.append(NodesTree(taxid=taxid, name=tree[taxid][0], parent=tree[taxid][1], rank=tree[taxid][2]))
                if index % self.flush_size == 0:
                    db_session.add_all(taxid_records)
                    print "flushing taxid recoreds to db %d" % index
                    db_session.flush()
                    db_session.commit()
                    taxid_records = []
        db_session.add_all(taxid_records)

    def import_gi_tax(self, db_session):
        index=0
        gi_records = []
        print "Start update Gi2taxid table."
        for line in open(self.gi2taxid_file, 'r'):
            gi, taxid = line.strip().split("\t")
            gi, taxid = int(gi), int(taxid)
            if self.create or (not self.create and not db_session.query(Gi2taxid).filter(Gi2taxid.gi == gi).all()):
                index+=1
                gi_records.append(Gi2taxid(gi=gi, taxid=taxid))
                if index % self.flush_size == 0:
                    db_session.add_all(gi_records)
                    print "flushing gi recoreds to db %d" % index
                    db_session.flush()
                    db_session.commit()
                    gi_records = []
        db_session.add_all(gi_records)

    def update_db(self):
        if self.create:
            engine = create_engine(self.db, echo=True)
            Base.metadata.create_all(engine)
        with Session(self.db, 60) as db_session:
            self.import_names_nodes(db_session)
        with Session(self.db, 60) as db_session:#open new session in order to enable commit in end of the previous session
            self.import_gi_tax(db_session)

class Query(object):
    def __init__(self, db_session):
        self.db_session = db_session

    def gi2name(self, gi):
        gi_record = self.db_session.query(Gi2taxid).filter(Gi2taxid.gi == gi).first()
        if gi_record and gi_record.node:
            return gi_record.node.name
        else:
            return None