import os
import re
from IPython.display import display, Markdown, HTML

from tf.fabric import Fabric

ORG = 'etcbc'

URL_GH = 'https://github.com'
URL_NB = 'http://nbviewer.jupyter.org/github'

CORPUS = 'bhsa'

SHEBANQ_URL = 'https://shebanq.ancient-data.org/hebrew'
SHEBANQ = (
    f'{SHEBANQ_URL}/text'
    '?book={book}&chapter={chapter}&verse={verse}&version={version}'
    '&mr=m&qw=q&tp=txt_p&tr=hb&wget=v&qget=v&nget=vt'
)
SHEBANQ_LEX = (f'{SHEBANQ_URL}/word' '?version={version}&id={lid}')

LIMIT_SHOW = 100
LIMIT_TABLE = 2000

CSS = '''
<style type="text/css">
.verse {
    display: flex;
    flex-flow: row wrap;
    direction: rtl;
}
.vl {
    display: flex;
    flex-flow: column nowrap;
    direction: ltr;
}
.sentence,.clause,.phrase {
    margin-top: -1.2em;
    margin-left: 1em;
    background: #ffffff none repeat scroll 0 0;
    padding: 0 0.3em;
    border-style: solid;
    border-radius: 0.2em;
    font-size: small;
    display: block;
    width: fit-content;
    max-width: fit-content;
    direction: ltr;
}
.atoms {
    display: flex;
    flex-flow: row wrap;
    margin: 0.3em;
    padding: 0.3em;
    direction: rtl;
    background-color: #ffffff;
}
.satom,.catom,.patom {
    margin: 0.3em;
    padding: 0.3em;
    border-radius: 0.3em;
    border-style: solid;
    display: flex;
    flex-flow: column nowrap;
    direction: rtl;
    background-color: #ffffff;
}
.sentence {
    border-color: #aa3333;
    border-width: 1px;
}
.clause {
    border-color: #aaaa33;
    border-width: 1px;
}
.phrase {
    border-color: #33aaaa;
    border-width: 1px;
}
.satom {
    border-color: #aa3333;
    border-width: 4px;
}
.catom {
    border-color: #aaaa33;
    border-width: 3px;
}
.patom {
    border-color: #33aaaa;
    border-width: 3px;
}
.word {
    padding: 0.1em;
    margin: 0.1em;
    border-radius: 0.1em;
    border: 1px solid #cccccc;
    display: flex;
    flex-flow: column nowrap;
    direction: rtl;
    background-color: #ffffff;
}
.lex {
    padding: 0.1em;
    margin: 0.1em;
    border-radius: 0.1em;
    border: 2px solid #888888;
    width: fit-content;
    display: flex;
    flex-flow: column nowrap;
    direction: rtl;
    background-color: #ffffff;
}
.satom.l,.catom.l,.patom.l {
    border-left-style: dotted
}
.satom.r,.catom.r,.patom.r {
    border-right-style: dotted
}
.satom.L,.catom.L,.patom.L {
    border-left-style: none
}
.satom.R,.catom.R,.patom.R {
    border-right-style: none
}
.h,.h :visited,.h :link {
    font-family: "Ezra SIL", "SBL Hebrew", sans-serif;
    font-size: large;
    color: #000044;
    direction: rtl;
    text-decoration: none;
}
.hb,.hb :visited,.hb :link {
    font-family: "Ezra SIL", "SBL Hebrew", sans-serif;
    font-size: large;
    direction: rtl;
    text-decoration: none;
}
.rela,.function,.typ {
    font-family: monospace;
    font-size: small;
    color: #0000bb;
}
.sp,.sp :visited,.sp :link {
    font-family: monospace;
    font-size: medium;
    color: #0000bb;
    text-decoration: none;
}
.vl {
    font-family: monospace;
    font-size: medium;
    color: #0000bb;
}
.vvs {
    font-family: monospace;
    font-size: medium;
    font-weight: bold;
    color: #0000bb;
}
.vvt {
    font-family: monospace;
    font-size: medium;
    color: #0000bb;
}
.gl {
    font-family: sans-serif;
    font-size: small;
    color: #aaaaaa;
}
.vs {
    font-family: sans-serif;
    font-size: small;
    font-weight: bold;
    color: #444444;
}
.nd {
    font-family: monospace;
    font-size: x-small;
    color: #999999;
}
.feat {
    font-family: monospace;
    font-size: medium;
    font-weight: bold;
    color: #0a6611;
}
.feat .f {
    font-family: sans-serif;
    font-size: x-small;
    color: #5555bb;
}
.hl {
    background-color: #ffee66;
}
</style>
'''

CSS_FONT = '<link rel="stylesheet" href="/data/static/fonts.css"/>'

CLASS_NAMES = dict(
    verse='verse',
    sentence='atoms',
    sentence_atom='satom',
    clause='atoms',
    clause_atom='catom',
    phrase='atoms',
    phrase_atom='patom',
    subphrase='subphrase',
    word='word',
    lex='lex',
)

ATOMS = dict(
    sentence_atom='sentence',
    clause_atom='clause',
    phrase_atom='phrase',
)
SUPER = dict((y, x) for (x, y) in ATOMS.items())

SECTION = {'book', 'chapter', 'verse', 'half_verse'}

NONE_VALUES = {None, 'NA', 'none', 'unknown'}

STANDARD_FEATURES = '''
    sp vs vt
    lex language gloss voc_lex voc_lex_utf8
    function typ rela
    number label book
'''

# for 4, 4b: voc_lex => g_lex, voc_lex_utf8 => g_lex_utf8


def dm(md):
  display(Markdown(md))


def _outLink(text, href, title=None):
  titleAtt = '' if title is None else f' title="{title}"'
  return f'<a target="_blank" href="{href}"{titleAtt}>{text}</a>'


class Bhsa(object):
  def __init__(
      self,
      api,
      name,
      version='c',
      locations=None,
      modules=None,
      asApi=False,
  ):
    self.asApi = asApi
    self.version = version
    standardFeatures = (
        STANDARD_FEATURES.replace('voc_', 'g_') if version in {'4', '4b'} else STANDARD_FEATURES
    )
    self.standardFeatures = set(standardFeatures.strip().split())

    if asApi:
      TF = Fabric(locations=locations, modules=modules, silent=True)
      api = TF.load('', silent=True)
      allFeatures = TF.explore(silent=True, show=True)
      loadableFeatures = allFeatures['nodes'] + allFeatures['edges']
      TF.load(loadableFeatures, add=True, silent=True)
    else:
      api.TF.load(self.standardFeatures, add=True, silent=True)
    self.prettyFeaturesLoaded = self.standardFeatures
    self.prettyFeatures = ()
    self.api = api
    self.cwd = os.getcwd()
    cwdPat = re.compile(f'^.*/github/([^/]+)/([^/]+)((?:/.+)?)$', re.I)
    cwdRel = cwdPat.findall(self.cwd)

    if not asApi:
      if cwdRel:
        (thisOrg, thisRepo, thisPath) = cwdRel[0]
        onlineTail = (f'{thisOrg}/{thisRepo}' f'/blob/master{thisPath}/{name}.ipynb')
      else:
        cwdRel = None
      nbUrl = (None if name is None or cwdRel is None else f'{URL_NB}/{onlineTail}')
      ghUrl = (None if name is None or cwdRel is None else f'{URL_GH}/{onlineTail}')
    docUrl = f'https://etcbc.github.io/bhsa'
    tutUrl = f'{URL_NB}/{ORG}/{CORPUS}/blob/master/tutorial/search.ipynb'
    extraUrl = f'https://dans-labs.github.io/text-fabric/Api/Bhsa/'
    dataLink = _outLink(CORPUS.upper(), docUrl, '{provenance of this corpus}')
    featureLink = _outLink(
        'Feature docs', f'{docUrl}/features/hebrew/{self.version}/0_home.html',
        '{CORPUS.upper()} feature documentation'
    )
    bhsaLink = _outLink('BHSA API', extraUrl, 'BHSA API documentation')
    tfLink = _outLink(
        f'Text-Fabric API {api.TF.version}', 'https://dans-labs.github.io/text-fabric/Api/General/',
        'text-fabric-api'
    )
    tfsLink = _outLink(
        'Search Reference',
        'https://dans-labs.github.io/text-fabric/Api/General/#search-templates',
        'Search Templates Introduction and Reference'
    )
    tutLink = _outLink(
        'Search tutorial', tutUrl,
        'Search tutorial in Jupyter Notebook'
    )
    if asApi:
      self.dataLink = dataLink
      self.featureLink = featureLink
      self.tfsLink = tfsLink
      self.tutLink = tutLink
    else:
      dm('**Documentation:**' f' {dataLink} {featureLink} {bhsaLink} {tfLink} {tfsLink}')
      if nbUrl:
        dm(
            f'''
This notebook online:
{_outLink('NBViewer', nbUrl)}
{_outLink('GitHub', ghUrl)}
'''
        )

    if not asApi:
      self.loadCSS()

  def loadCSS(self):
    asApi = self.asApi
    if asApi:
      return CSS_FONT + CSS
    display(HTML(CSS))

  def header(self):
    return f'''
      <img class="hdlogo" src="/data/static/logo.png"/>
      <div class="hdlinks">
        {self.dataLink}
        {self.featureLink}
        {self.tfsLink}
        {self.tutLink}
      </div>
      <img class="hdlogo" src="/server/static/logo.png"/>
    '''

  def shbLink(self, n, text=None, asString=False):
    api = self.api
    L = api.L
    T = api.T
    F = api.F
    version = self.version
    nType = F.otype.v(n)
    if nType == 'lex':
      lex = F.lex.v(n)
      lan = F.language.v(n)
      lexId = '{}{}'.format(
          '1' if lan == 'Hebrew' else '2',
          lex.replace('>', 'A').replace('<', 'O').replace('[', 'v').replace('/',
                                                                            'n').replace('=', 'i'),
      )
      href = SHEBANQ_LEX.format(
          version=version,
          lid=lexId,
      )
      title = 'show this lexeme in SHEBANQ'
      if text is None:
        text = F.voc_lex_utf8.v(n)
      result = _outLink(text, href, title=title)
      if asString:
        return result
      display(HTML(result))
      return

    (bookE, chapter, verse) = T.sectionFromNode(n)
    bookNode = n if nType == 'book' else L.u(n, otype='book')[0]
    book = F.book.v(bookNode)
    passageText = (
        bookE if nType == 'book' else '{} {}'.format(bookE, chapter)
        if nType == 'chapter' else '{} {}:{}{}'.format(bookE, chapter, verse, F.label.v(n))
        if nType == 'half_verse' else '{} {}:{}'.format(bookE, chapter, verse)
    )
    href = SHEBANQ.format(
        version=version,
        book=book,
        chapter=chapter,
        verse=verse,
    )
    if text is None:
      text = passageText
      title = 'show this passage in SHEBANQ'
    else:
      title = passageText
    result = _outLink(text, href, title=title)
    if asString:
      return result
    display(HTML(result))

  def plain(
      self,
      n,
      linked=True,
      withNodes=False,
      asString=False,
  ):
    asApi = self.asApi
    api = self.api
    L = api.L
    T = api.T
    F = api.F

    nType = F.otype.v(n)
    result = ''
    if asApi:
      nodeRep = f' <span class="nd">{n}</span> ' if withNodes else ''
    else:
      nodeRep = f' *{n}* ' if withNodes else ''

    hebrew = True
    if nType == 'word':
      rep = T.text([n])
      if linked:
        rep = self.shbLink(n, text=rep, asString=True)
    elif nType in SECTION:
      fmt = ('{}' if nType == 'book' else '{} {}' if nType == 'chapter' else '{} {}:{}')
      rep = fmt.format(*T.sectionFromNode(n))
      hebrew = False
      if nType == 'half_verse':
        rep += F.label.v(n)
      if linked:
        rep = self.shbLink(n, text=rep, asString=True)
    elif nType == 'lex':
      rep = F.voc_lex_utf8.v(n)
      if linked:
        rep = self.shbLink(n, text=rep, asString=True)
    else:
      rep = T.text(L.d(n, otype='word'))
      if linked:
        rep = self.shbLink(n, text=rep, asString=True)

    if hebrew:
      rep = f'<span class="hb">{rep}</span>'
    result = f'{rep}{nodeRep}'

    if asString or asApi:
      return result
    dm((result))

  def plainTuple(
      self,
      ns,
      seqNumber,
      position=None,
      opened=False,
      linked=1,
      withNodes=False,
      asString=False,
  ):
    asApi = self.asApi
    api = self.api
    F = api.F
    if asApi:
      pretty = self.prettyTuple(
          ns, seqNumber,
          withNodes=withNodes,
      ) if opened else ''
      current = ' focus' if seqNumber == position else ''
      attOpen = ' open ' if opened else ''
      html = (
          f'''
    <div class="dtrow{current}">
        <details class="pretty" seq="{seqNumber}" {attOpen}>
          <summary>{seqNumber}</summary>
          <div class="pretty">
            {pretty}
          </div>
        </details>
  '''
          +
          ''.join(
              f'''<div>{self.plain(
                          n,
                          linked=i == linked - 1,
                          withNodes=withNodes,
                        ).replace("|", "&#124;")
                      }
                  </div>
              '''
              for (i, n) in enumerate(ns)
          )
          +
          '''
    </div>
  '''
      )
      return html
    markdown = [str(seqNumber)]
    for (i, n) in enumerate(ns):
      markdown.append(
          self.plain(
              n,
              linked=i == linked - 1,
              withNodes=withNodes,
              asString=True,
          ).replace('|', '&#124;')
      )
    markdown = '|'.join(markdown)
    if asString:
      return markdown
    head = ['n | ' + (' | '.join(F.otype.v(n) for n in ns))]
    head.append(' | '.join('---' for n in range(len(ns) + 1)))
    head.append(markdown)

    dm('\n'.join(head))

  def table(
      self,
      results,
      start=None,
      end=None,
      linked=1,
      withNodes=False,
      asString=False,
  ):
    api = self.api
    F = api.F

    collected = []
    if start is None:
      start = 1
    i = -1
    rest = 0
    if not hasattr(results, '__len__'):
      if end is None or end - start + 1 > LIMIT_SHOW:
        end = start - 1 + LIMIT_SHOW
      for result in results:
        i += 1
        if i < start - 1:
          continue
        if i >= end:
          break
        collected.append((i + 1, result))
    else:
      typeResults = type(results)
      if typeResults is set or typeResults is frozenset:
        results = sorted(results)
      if end is None or end > len(results):
        end = len(results)
      rest = 0
      if end - (start - 1) > LIMIT_TABLE:
        rest = end - (start - 1) - LIMIT_TABLE
        end = start - 1 + LIMIT_TABLE
      for i in range(start - 1, end):
        collected.append((i + 1, results[i]))

    if len(collected) == 0:
      return
    (firstSeq, firstResult) = collected[0]
    nColumns = len(firstResult)
    markdown = ['n | ' + (' | '.join(F.otype.v(n) for n in firstResult))]
    markdown.append(' | '.join('---' for n in range(nColumns + 1)))
    for (seqNumber, ns) in collected:
      markdown.append(
          self.plainTuple(
              ns,
              seqNumber,
              linked=linked,
              withNodes=withNodes,
              asString=True,
          )
      )
    markdown = '\n'.join(markdown)
    if asString:
      return markdown
    dm(markdown)
    if rest:
      dm(
          f'**{rest} more results skipped** because we show a maximum of'
          f' {LIMIT_TABLE} results at a time'
      )

  def prettySetup(self, features=None, noneValues=None):
    if features is None:
      self.prettyFeatures = ()
    else:
      featuresRequested = (tuple(features.strip().split()
                                 )) if type(features) is str else tuple(features)
      tobeLoaded = set(featuresRequested) - self.prettyFeaturesLoaded
      if tobeLoaded:
        self.api.TF.load(tobeLoaded, add=True, silent=True)
        self.prettyFeaturesLoaded |= tobeLoaded
      self.prettyFeatures = featuresRequested
    if noneValues is None:
      self.noneValues = NONE_VALUES
    else:
      self.noneValues = noneValues

  def pretty(
      self,
      n,
      withNodes=False,
      suppress=set(),
      highlights={},
  ):
    asApi = self.asApi
    html = []
    if type(highlights) is set:
      highlights = {m: '' for m in highlights}
    self._pretty(
        n,
        html,
        firstSlot=None,
        lastSlot=None,
        withNodes=withNodes,
        suppress=suppress,
        highlights=highlights,
    )
    htmlStr = '\n'.join(html)
    if asApi:
      return htmlStr
    display(HTML(htmlStr))

  def prettyTuple(
      self,
      ns,
      seqNumber,
      item='Result',
      withNodes=False,
      suppress=set(),
      colorMap=None,
      highlights=None,
  ):
    asApi = self.asApi
    api = self.api
    L = api.L
    F = api.F
    sortNodes = api.sortNodes
    verses = set()
    lexemes = set()
    newHighlights = {}
    if type(highlights) is set:
      highlights = {m: '' for m in highlights}
    if highlights:
      newHighlights.update(highlights)
    for (i, n) in enumerate(ns):
      thisHighlight = None
      if highlights is not None:
        thisHighlight = highlights.get(n, None)
      elif colorMap is not None:
        thisHighlight = colorMap.get(i + 1, None)
      else:
        thisHighlight = ''

      nType = F.otype.v(n)
      if nType not in SECTION:
        firstSlot = n if nType == 'word' else L.d(n, otype='word')[0]
        if nType == 'lex':
          lexemes.add(n)
          if thisHighlight is not None:
            newHighlights[n] = thisHighlight
        else:
          verses.add(L.u(firstSlot, otype='verse')[0])
          atomType = SUPER.get(nType, None)
          if atomType:
            if thisHighlight is not None:
              for m in L.d(n, otype=atomType):
                newHighlights[m] = thisHighlight
          else:
            if thisHighlight is not None:
              newHighlights[n] = thisHighlight
    if not asApi:
      dm(f'''
##### {item} {seqNumber}
''')
    if asApi:
      html = []
    for l in sortNodes(lexemes):
      h = self.pretty(
          l,
          withNodes=withNodes,
          suppress=suppress,
          highlights=newHighlights,
      )
      if asApi:
        html.append(h)
    for v in sortNodes(verses):
      h = self.pretty(
          v,
          withNodes=withNodes,
          suppress=suppress,
          highlights=newHighlights,
      )
      if asApi:
        html.append(h)
    if asApi:
      return '\n'.join(html)

  def show(
      self,
      results,
      condensed=True,
      start=None,
      end=None,
      withNodes=False,
      suppress=set(),
      colorMap=None,
      highlights=None,
  ):
    newHighlights = None
    if type(highlights) is set:
      highlights = {m: '' for m in highlights}
    if highlights:
      newHighlights = {}
      newHighlights.update(highlights)
    if condensed:
      if colorMap is not None:
        if newHighlights is None:
          newHighlights = {}
        for ns in results:
          for (i, n) in enumerate(ns):
            thisHighlight = None
            if highlights is not None:
              thisHighlight = highlights.get(n, None)
            elif colorMap is not None:
              thisHighlight = colorMap.get(i + 1, None)
            else:
              thisHighlight = ''
            newHighlights[n] = thisHighlight

      (passages, verses) = self.condense(results)
      results = passages if len(verses) == 0 else verses

    if start is None:
      start = 1
    i = -1
    if not hasattr(results, '__len__'):
      if end is None or end - start + 1 > LIMIT_SHOW:
        end = start - 1 + LIMIT_SHOW
      for result in results:
        i += 1
        if i < start - 1:
          continue
        if i >= end:
          break
        self.prettyTuple(
            result,
            i + 1,
            item='Verse' if condensed else 'Result',
            withNodes=withNodes,
            suppress=suppress,
            colorMap=colorMap,
            highlights=newHighlights,
        )
    else:
      if end is None or end > len(results):
        end = len(results)
      rest = 0
      if end - (start - 1) > LIMIT_SHOW:
        rest = end - (start - 1) - LIMIT_SHOW
        end = start - 1 + LIMIT_SHOW
      for i in range(start - 1, end):
        self.prettyTuple(
            results[i],
            i + 1,
            item='Passage' if condensed else 'Result',
            withNodes=withNodes,
            suppress=suppress,
            colorMap=colorMap,
            highlights=newHighlights,
        )
      if rest:
        dm(
            f'**{rest} more results skipped** because we show a maximum of'
            f' {LIMIT_SHOW} results at a time'
        )

  def search(self, query, silent=False, sets=None, shallow=False):
    api = self.api
    info = api.info
    S = api.S
    results = S.search(query, sets=sets, shallow=shallow)
    if not shallow:
      results = sorted(results)
    nResults = len(results)
    plural = '' if nResults == 1 else 's'
    if not silent:
      info(f'{nResults} result{plural}')
    return results

  def condense(self, results):
    asApi = self.asApi
    api = self.api
    F = api.F
    L = api.L
    sortNodes = api.sortNodes
    verses = {}
    passages = set()
    for ns in results:
      for n in ns:
        nType = F.otype.v(n)
        if nType in SECTION:
          if nType == 'verse':
            verses.setdefault(n, set())
          passages.add(n)
        else:
          fw = n if nType == 'word' else L.d(n, otype='word')[0]
          v = L.u(fw, otype='verse')[0]
          verses.setdefault(v, set()).add(n)
    passages = tuple(sortNodes(passages))
    verses = tuple((p, ) + tuple(verses[p]) for p in sortNodes(verses))
    return verses if asApi else (passages, verses)

  def _pretty(
      self,
      n,
      html,
      firstSlot=None,
      lastSlot=None,
      withNodes=True,
      suppress=set(),
      highlights={},
  ):
    api = self.api
    L = api.L
    T = api.T
    F = api.F
    sortNodes = api.sortNodes
    hl = highlights.get(n, None)
    hlClass = ''
    hlStyle = ''
    if hl == '':
      hlClass = ' hl'
    else:
      hlStyle = f' style="background-color: {hl};"'

    nType = F.otype.v(n)
    className = CLASS_NAMES.get(nType, None)
    superType = ATOMS.get(nType, None)
    boundaryClass = ''
    (myStart, myEnd) = (n, n) if nType == 'word' else self._getBoundary(n)
    if superType:
      (superNode, superStart, superEnd) = self._getSuper(n, superType)
      if superStart < myStart:
        boundaryClass += ' r'
      if superEnd > myEnd:
        boundaryClass += ' l'
    if ((firstSlot and myEnd < firstSlot) or (lastSlot and myStart > lastSlot)):  # noqa 129
      return
    if firstSlot and (myStart < firstSlot):
      boundaryClass += ' R'
    if lastSlot and (myEnd > lastSlot):
      boundaryClass += ' L'
    if nType == 'book':
      html.append(self.shbLink(n, asString=True))
      return
    elif nType == 'chapter':
      html.append(self.shbLink(n, asString=True))
      return
    elif nType in {'verse', 'half_verse'}:
      label = self.shbLink(n, asString=True)
      (firstSlot, lastSlot) = self._getBoundary(n)
      children = sortNodes(
          set(L.d(n, otype='sentence_atom')) | {
              L.u(firstSlot, otype='sentence_atom')[0],
              L.u(lastSlot, otype='sentence_atom')[0],
          }
      )
    elif nType == 'sentence':
      children = L.d(n, otype='sentence_atom')
    elif nType == 'sentence_atom' or nType == 'clause':
      children = L.d(n, otype='clause_atom')
    elif nType == 'clause_atom' or nType == 'phrase':
      children = L.d(n, otype='phrase_atom')
    elif nType == 'phrase_atom' or nType == 'subphrase':
      children = L.d(n, otype='word')
    elif nType == 'lex':
      children = ()
    elif nType == 'word':
      children = ()
      lx = L.u(n, otype='lex')[0]
    html.append(f'<div class="{className} {boundaryClass}{hlClass}"{hlStyle}>')
    if nType in {'verse', 'half_verse'}:
      nodePart = f'<div class="nd">{n}</div>' if withNodes else ''
      html.append(
          f'''
    <div class="vl">
        <div class="vs">{label}</div>{nodePart}
    </div>
'''
      )
    elif nType == 'word':
      nodePart = f'<div class="nd">{n}</div>' if withNodes else ''
      if nodePart:
        html.append(nodePart)
      lx = L.u(n, otype='lex')[0]
      lexLink = (self.shbLink(lx, text=T.text([n]), asString=True))
      html.append(f'<div class="h">{lexLink}</div>')
      if 'sp' not in suppress:
        spLink = (self.shbLink(n, text=F.sp.v(n), asString=True))
        html.append(f'<div class="sp">{spLink}</div>')
      if 'gloss' not in suppress:
        html.append(f'<div class="gl">' f'{F.gloss.v(lx).replace("<", "&lt;")}</div>')
      if F.sp.v(n) == 'verb':
        if 'vs' not in suppress:
          html.append(f'<div class="vvs">{F.vs.v(n)}</div>')
        if 'vt' not in suppress:
          html.append(f'<div class="vvt">{F.vt.v(n)}</div>')
      self._extraFeatures(n, suppress, html)
    elif nType == 'lex':
      nodePart = f'<div class="nd">{n}</div>' if withNodes else ''
      if nodePart:
        html.append(nodePart)
      html.append(f'<div class="h">{F.voc_lex_utf8.v(n)}</div>')
      if 'voc_lex' not in suppress:
        llink = self.shbLink(n, text=F.voc_lex.v(n).replace("<", "&lt;"), asString=True)
        html.append(f'<div class="vl">{llink}</div>')
      if 'gloss' not in suppress:
        html.append(f'<div class="gl">' f'{F.gloss.v(n).replace("<", "&lt;")}</div>')
      self._extraFeatures(n, suppress, html)
    elif superType:
      nodePart = (f'<span class="nd">{superNode}</span>' if withNodes else '')
      typePart = self.shbLink(superNode, text=superType, asString=True)
      featurePart = []
      if superType == 'clause':
        if 'rela' not in suppress:
          featurePart.append(f' <span class="rela">{F.rela.v(superNode)}</span>')
        if 'typ' not in suppress:
          featurePart.append(f' <span class="typ">{F.typ.v(superNode)}</span>')
      elif superType == 'phrase':
        if 'function' not in suppress:
          featurePart.append(f' <span class="function">' f'{F.function.v(superNode)}</span>')
        if 'typ' not in suppress:
          featurePart.append(f' <span class="typ">{F.typ.v(superNode)}</span>')
      self._extraFeatures(n, suppress, featurePart)
      featurePart = '\n'.join(featurePart)
      shl = highlights.get(superNode, None)
      shlClass = ''
      shlStyle = ''
      if shl == '':
        shlClass = ' hl'
      else:
        shlStyle = f' style="background-color: {shl};"'
      html.append(
          f'''
    <div class="{superType}{shlClass}"{shlStyle}>
        {typePart} {nodePart} {featurePart}
    </div>
    <div class="atoms">
'''
      )
    for ch in children:
      self._pretty(
          ch,
          html,
          firstSlot=firstSlot,
          lastSlot=lastSlot,
          withNodes=withNodes,
          suppress=suppress,
          highlights=highlights,
      )
    if superType:
      html.append('''
    </div>
''')
    html.append('''
</div>
''')

  def _extraFeatures(self, n, suppress, html):
    api = self.api
    Fs = api.Fs
    for ef in self.prettyFeatures:
      if ef not in suppress:
        efVal = Fs(ef).v(n)
        if efVal not in self.noneValues:
          html.append(f'<div class="feat"><span class="f">{ef}=' f'</span>{efVal}</div>')

  def _getBoundary(self, n):
    api = self.api
    L = api.L
    words = L.d(n, otype='word')
    return (words[0], words[-1])

  def _getSuper(self, n, tp):
    api = self.api
    L = api.L
    superNode = L.u(n, otype=tp)[0]
    return (superNode, *self._getBoundary(superNode))
