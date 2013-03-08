import ply.lex as lexer
import ply.yacc as yacc


"""
Implementacion de un analizador lexico (lexer) y un analizador sintactico 
(parser) a partir de las reglas de un sencillo lenguaje (funcional, similar
a ML) definidas en la gramatica 5.1 del libro "Basics of Compiler Design", 
utilizando PLY.

- Basics of Compiler Design, Torben AE. Mogensen - :
http://www.diku.dk/hjemmesider/ansatte/torbenm/Basics/

- PLY (Python Lex-Yacc) - :
http://www.dabeaz.com/ply/

Gramatica:
	Program     ->  Funs

	Funs        ->  Fun
	Funs        ->  Fun Funs

	Fun         ->  TypeId ( TypeIds ) = Exp

	TypeId      ->  int id
	TypeId      ->  bool id

	TypeIds     ->  TypeId
	TypeIds     ->  TypeId , TypeIds

	Exp         ->  num
	Exp         ->  id
	Exp         ->  Exp + Exp
	Exp         ->  if Exp then Exp else Exp
	Exp         ->  id ( Exps )
	Exp         ->  let id = Exp in Exp

	Exps        ->  Exp
	Exps        ->  Exp , Exps

TODO corregir 8 conflictos shift/reduce de la gramatica


El autor de esta implementacion anhade ademas las siguientes reglas:
	Fun         ->  TypeId ( ) = Exp
	Exp         ->  BValue
	BValue      ->  true
	BValue      ->  false


Sergio Salomon Garcia   <sergio.salomon at alumnos.unican.es>
"""


class Lexing():
	"""
	Analizador lexico para la gramatica dada.
	"""

	keywords = {'int': 'INT', 'bool': 'BOOL', 'true': 'TRUE', 'false': 'FALSE',
		'let': 'LET', 'in': 'IN', 'if': 'IF', 'then': 'THEN', 'else': 'ELSE'}
	tokens = ('OPENBRACK', 'CLOSEBRACK', 'PLUS', 'EQUAL', 'NAMEVAR',
		'NUMBER', 'COMMA') + tuple(keywords.values())

	t_OPENBRACK = '\('
	t_CLOSEBRACK = '\)'
	t_PLUS = '\+'
	t_EQUAL = '\='
	t_COMMA = ','


	def t_NUMBER(self, t):
		r'[0-9]+'
		t.type = 'NUMBER'
		t.value = int(t.value)
		return t

	def t_NAMEVAR(self, t):
		r'[A-Za-z][A-Za-z0-9\_]*'
		t.type = self.keywords.get(t.value , 'NAMEVAR')
		return t

	def t_ANY_newline(self, t):
		r'[\n\r]+'
		t.lexer.lineno += len(t.value)

	def t_ANY_newspace(self, t):
		r'[ \t]+'
		pass

	def t_ANY_error(self, t):
		print "No se reconoce '%s' en la linea '%s' y\
		 el caracter %s" % (t.value[0], t.lexer.lineno, t.lexer.lexpos)
		t.lexer.skip(1)

	########

	def build(self, **kwargs):
		self.lexer = lexer.lex(module = self, **kwargs)
		self.lexer.posicion = 1

	def input(self, data):
		self.lexer.input(data)

	def token(self):
		return self.lexer.token()

	def test(self, data):
		result = ""

		self.lexer.input(data)
		while True:
			tok = lexer.token()
			if not tok: break
			result = result + "\n" + str(tok)

		return result.strip()



class Parsing():
	"""
	Analizador sintactico para la gramatica dada.
	"""

	tokens = Lexing.tokens
	start = 'program'

	def p_program(self, p):
		"""
		program : funs
		"""
		pass

	def p_funs(self, p):
		"""
		funs : fun funs
		| fun
		"""
		pass

	def p_fun(self, p):
		"""
		fun : type_id OPENBRACK type_ids CLOSEBRACK EQUAL exp
		| type_id OPENBRACK CLOSEBRACK EQUAL exp
		"""
		pass

	def p_type_id(self, p):
		"""
		type_id : INT NAMEVAR
		| BOOL NAMEVAR
		"""

	def p_type_ids(self, p):
		"""
		type_ids : type_id
		| type_id COMMA type_ids
		"""
		pass

	def p_exp(self, p):
		"""
		exp : NUMBER
		| NAMEVAR
		| b_value
		| exp PLUS exp
		| exp EQUAL exp
		| IF exp THEN exp ELSE exp
		| NAMEVAR OPENBRACK exps CLOSEBRACK
		| LET NAMEVAR EQUAL exp IN exp
		"""
		pass

	def p_exps(self, p):
		"""
		exps : exp
		| exp COMMA exps
		"""
		pass

	def p_b_value(self, p):
		"""
		b_value : TRUE
		| FALSE
		"""
		pass

	########

	def p_error(self, p):
		print("Syntax error at '%s' (line: %s)" % (p.value, p.lineno))
		# TODO error con p.value cuando *falta* un token

	def run(self, s):
		lexico = Lexing()
		lexico.build()
		global tokens   # TODO error que obliga llamar a build() de nuevo ?
		self.parser = yacc.yacc(debug = True, module = self)
		result = self.parser.parse(s, lexico)
		return result



class Compiler():
	"""
	Compilador parcial que utiliza los analizadores
	lexico y sintactico implementados.
	"""

	def __init__(self):
		self.lex = Lexing()
		self.parse = Parsing()
		self.separator = "-" * 32
		self.lex.build()

	def init(self):
		self.lex.build()

	def compile(self, code_file, verbose=False):
		try:
			with open(code_file) as f:
				# lee el fichero
				text = f.read()

				# realiza el analisis lexico
				print "---- Lexical analysis ----"
				result = self.lex_analysis(text)
				if verbose: self.__show_result(result)

				# realiza el analisis sintactivo
				print "---- Syntax analysis ----"
				result = self.pars_analysis(text)
				if result is not None: 
					self.__show_result(result)
				elif verbose: 
					self.__show_result("No errors in the code.")
		except Exception, e:
			print "ERROR compilando el archivo ::::", str(e)

	def lex_analysis(self, text):
		return self.lex.test(text)

	def pars_analysis(self, text):
		return self.parse.run(text)

	def __show_result(self, t):
		print t, "\n", self.separator


#################

#######
## TESTING:

if __name__ == '__main__':

	simple_compiler = Compiler()
	code_file = "prueba.ml"

	# pruebas sencillas con palabras del lenguaje
	"""
	code = "5 + 5 = 3 \n int foo"
	print "Analizado lexico:", "\n\t", code
	print simple_compiler.lex_analysis(code)
	print

	code = "int func() = 4 + 8"
	print "Errores en la sintaxis:", "\n\t", code
	print simple_compiler.pars_analysis(code)
	print
	"""


	# compilacion de un fichero de codigo de prueba
	print "Compilacion:"
	try:
		f = open(code_file)
		for line in f.readlines():
			print "\t", line,
		f.close()
	except Exception, e:
		raise e

	simple_compiler.init()
	simple_compiler.compile(code_file, True)



