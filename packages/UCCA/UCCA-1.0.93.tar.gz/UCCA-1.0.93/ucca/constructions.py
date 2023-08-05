from collections import OrderedDict

from ucca import textutil, layer0, layer1
from ucca.layer1 import EdgeTags, NodeTags


class Construction:
    def __init__(self, name, description, criterion, default=False):
        """
        :param name: short name
        :param description: long description
        :param criterion: predicate function to apply to a Candidate, saying if it is an instance of this construction
        :param default: whether this construction is included in evaluation by default
        """
        self.name = name
        self.description = description
        self.criterion = criterion
        self.default = default

    def __str__(self):
        return self.name

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, other):
        return self.name == (other.name if isinstance(other, Construction) else other)

    def __call__(self, candidate):
        if self.criterion(candidate):
            yield self


CATEGORIES_NAME = "categories"
CATEGORY_DESCRIPTIONS = {v: k for k, v in EdgeTags.__dict__.items() if not k.startswith("_")}


class Categories(Construction):
    def __init__(self):
        super().__init__(CATEGORIES_NAME, description=None, criterion=None)

    def __call__(self, candidate):
        tag = candidate.edge.tag
        yield Construction(tag, CATEGORY_DESCRIPTIONS.get(tag, tag), criterion=None)


class Candidate:
    def __init__(self, edge, reference=None, verbose=False):
        self.edge = edge
        self.out_tags = {e.tag for e in edge.child}
        self.reference = reference
        self.verbose = verbose
        self.terminals = None
        self.extra = {}

    def _init_terminals(self, attr=None, annotate=False):
        if self.terminals is None:
            try:
                self.terminals = self.edge.child.get_terminals()
            except (AttributeError, ValueError):
                self.terminals = ()
            if self.reference is not None:
                # noinspection PyTypeChecker
                self.terminals = [self.reference.by_id(t.ID) for t in self.terminals]
            passage = self.edge.parent.root
            if annotate and not passage.extra.get("annotated"):
                textutil.annotate(passage, as_array=True, verbose=self.verbose)
                passage.extra["annotated"] = True
        if attr:
            ret = self.extra.get(attr)
            if ret is None:
                ret = self.extra[attr] = {t.get_annotation(attr, as_array=True) for t in self.terminals}
            return ret

    @property
    def remote(self):
        return self.edge.attrib.get("remote", False)

    @property
    def implicit(self):
        return self.edge.child.attrib.get("implicit", False)

    @property
    def excluded(self):
        return self.edge.tag in EXCLUDED_EDGE_TAGS or self.edge.child.tag in EXCLUDED_NODE_TAGS

    @property
    def pos(self):
        return self._init_terminals(attr=textutil.Attr.POS, annotate=True)

    @property
    def dep(self):
        return self._init_terminals(attr=textutil.Attr.DEP, annotate=True)

    @property
    def heads(self):
        attr = textutil.Attr.HEAD
        ret = self.extra.get(attr)
        if ret is None:
            self._init_terminals(annotate=True)
            positions = {t.para_pos for t in self.terminals}
            ret = self.extra[attr] = {t for t in self.terminals if int(t.tok[attr]) not in positions}
        return ret

    @property
    def tokens(self):
        attr = "tokens"
        ret = self.extra.get(attr)
        if ret is None:
            self._init_terminals()
            ret = self.extra[attr] = {t.text.lower() for t in self.terminals}
        return ret

    def is_primary(self):
        return not self.remote and not self.implicit and not self.excluded

    def is_remote(self):
        return self.remote and not self.implicit and not self.excluded

    def is_predicate(self):
        return self.edge.tag in {EdgeTags.Process, EdgeTags.State} and \
            self.out_tags <= {EdgeTags.Center, EdgeTags.Function, EdgeTags.Terminal} and \
            "to" not in self.tokens

    def constructions(self, constructions=None):
        for construction in constructions or CONSTRUCTIONS:
            yield from construction(self)


EXCLUDED_EDGE_TAGS = (EdgeTags.Punctuation,
                      EdgeTags.LinkArgument,
                      EdgeTags.LinkRelation,
                      EdgeTags.Terminal)

EXCLUDED_NODE_TAGS = (NodeTags.Linkage,
                      NodeTags.Punctuation,
                      layer0.NodeTags.Word,
                      layer0.NodeTags.Punct)


CONSTRUCTIONS = (
    Construction("primary", "Regular edges", Candidate.is_primary, default=True),
    Construction("remote", "Remote edges", Candidate.is_remote, default=True),
    Construction("aspectual_verbs", "Aspectual verbs",
                 lambda c: c.pos == {"VERB"} and c.edge.tag == EdgeTags.Adverbial),
    Construction("light_verbs", "Light verbs",
                 lambda c: c.pos == {"VERB"} and c.edge.tag == EdgeTags.Function),
    Construction("mwe", "Multi-word expressions",
                 lambda c: c.is_primary() and c.edge.child.tag == NodeTags.Foundational and len(
                     c.edge.child.terminals) > 1),  # Unanalyzable unit
    Construction("pred_nouns", "Predicate nouns",
                 lambda c: "ADJ" not in c.pos and "NOUN" in c.pos and c.is_predicate()),
    Construction("pred_adjs", "Predicate adjectives",
                 lambda c: "ADJ" in c.pos and "NOUN" not in c.pos and c.is_predicate()),
    Construction("expletives", "Expletives",
                 lambda c: c.tokens <= {"it", "there"} and c.edge.tag == EdgeTags.Function),
    Categories(),
)
PRIMARY = CONSTRUCTIONS[0]
CONSTRUCTION_BY_NAME = OrderedDict([(c.name, c) for c in CONSTRUCTIONS])
DEFAULT = OrderedDict((str(c), c) for c in CONSTRUCTIONS if c.default)


def add_argument(argparser, default=True):
    d = list(DEFAULT) if default else [n for n in CONSTRUCTION_BY_NAME if n not in DEFAULT]
    argparser.add_argument("--constructions", nargs="*", choices=CONSTRUCTION_BY_NAME, default=d, metavar="x",
                           help="construction types to include, out of {%s}" % ",".join(CONSTRUCTION_BY_NAME))


def get_by_name(name):
    return name if isinstance(name, Construction) else CATEGORY_DESCRIPTIONS.get(name) or CONSTRUCTION_BY_NAME[name]


def get_by_names(names=None):
    return list(map(get_by_name, names or ()))


def terminal_ids(passage):
    return {t.ID for t in passage.layer(layer0.LAYER_ID).all}


def diff_terminals(*passages):
    texts = [[t.text for t in p.layer(layer0.LAYER_ID).all] for p in passages]
    return [[t for t in texts[i] if t not in texts[j]] for i, j in ((0, 1), (1, 0))]


def extract_edges(passage, constructions=None, reference=None, verbose=False):
    """
    Find constructions in UCCA passage.
    :param passage: Passage object to find constructions in
    :param constructions: list of constructions to include or None for all
    :param reference: Passage object to get POS tags from (default: `passage')
    :param verbose: whether to print tagged text
    :return: dict of Construction -> list of corresponding edges
    """
    constructions = get_by_names(constructions)
    if reference is not None:
        ids1, ids2 = terminal_ids(passage), terminal_ids(reference)
        assert ids1 == ids2, "Reference passage terminals do not match: %s (%d != %d)\nDifference:\n%s" % (
            reference.ID, len(terminal_ids(passage)), len(terminal_ids(reference)),
            "\n".join(map(str, diff_terminals(passage, reference))))
    extracted = OrderedDict((c, []) for c in constructions)
    for node in passage.layer(layer1.LAYER_ID).all:
        for edge in node:
            candidate = Candidate(edge, reference=reference, verbose=verbose)
            for construction in candidate.constructions(constructions):
                extracted.setdefault(construction, []).append(edge)
    return extracted
