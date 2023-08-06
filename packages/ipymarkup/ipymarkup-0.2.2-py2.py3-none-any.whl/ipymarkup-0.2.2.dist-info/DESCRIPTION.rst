
ipymarkup 
=========

NER markup visualisation for Jupyter Notebook. 

::

  from ipymarkup import Span, AsciiMarkup

  text = 'a d a b a a a b c c c f d'
  spans = [
    Span(0, 13, 'a'),
    Span(2, 25, 'd'),
    Span(6, 15, 'b'),
    Span(16, 21, 'c'),
    Span(22, 23, 'f'),
  ]
  AsciiMarkup(text, spans)

  >>> a d a b a a a b c c c f d
  ... a------------ c---- f 
  ... d----------------------
  ... b-------- 


For more examples and explanation see `ipymarkup documentation <http://nbviewer.jupyter.org/github/natasha/ipymarkup/blob/master/docs.ipynb>`_.


