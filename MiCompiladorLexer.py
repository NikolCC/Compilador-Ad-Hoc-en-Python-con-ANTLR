from antlr4 import *
from MiCompiladorLexer import MiCompiladorLexer
from MiCompiladorParser import MiCompiladorParser
from MiCompiladorListener import MiCompiladorListener
from antlr4.error.ErrorListener import ErrorListener

# Manejo de errores personalizado
class CustomErrorListener(ErrorListener):
    def syntaxError(self, recognizer, offendingSymbol, line, column, msg, e):
        raise ValueError(f"Error sintáctico en la línea {line}, columna {column}: {msg}")

    def reportAmbiguity(self, recognizer, dfa, startIndex, stopIndex, exact, ambigAlts, configs):
        raise ValueError(f"Ambigüedad detectada entre las alternativas {ambigAlts}")

    def reportAttemptingFullContext(self, recognizer, dfa, startIndex, stopIndex, conflictingAlts, configs):
        raise ValueError(f"Intento de análisis de contexto completo entre las alternativas {conflictingAlts}")

    def reportContextSensitivity(self, recognizer, dfa, startIndex, stopIndex, prediction, configs):
        raise ValueError(f"Sensibilidad de contexto detectada en la posición {startIndex}-{stopIndex}, predicción: {prediction}")

# Optimizaciones
class OptimizedEvalVisitor(ParseTreeVisitor):
    def visitInicio(self, ctx):
        try:
            return self.visitExpresion(ctx.expresion())
        except Exception as e:
            print(f"Error de evaluación: {e}")
            return None

    def visitExpresion(self, ctx):
        left = self.visitTermino(ctx.termino(0))

        for i in range(1, len(ctx.termino())):
            op = ctx.getChild(2 * i - 1).getText()
            right = self.visitTermino(ctx.termino(i))

            if op == '+':
                left += right
            elif op == '-':
                left -= right

        return left

    def visitTermino(self, ctx):
        left = self.visitFactor(ctx.factor(0))

        for i in range(1, len(ctx.factor())):
            op = ctx.getChild(2 * i - 1).getText()
            right = self.visitFactor(ctx.factor(i))

            if op == '*':
                left *= right

        return left

    def visitFactor(self, ctx):
        if ctx.NUMERO():
            return int(ctx.NUMERO().getText())
        elif ctx.expresion():
            return self.visitExpresion(ctx.expresion())
        else:
            return 0  # Manejo básico de paréntesis

# Validación de seguridad
def validate_security(expression):
    # Implementa lógica de validación de seguridad aquí
    if "eval" in expression or "exec" in expression:
        raise SecurityError("Expresión insegura: contiene llamadas a eval o exec")

def main():
    input_stream = InputStream("2 * (3 + 4)")
    lexer = MiCompiladorLexer(input_stream)
    tokens = CommonTokenStream(lexer)
    parser = MiCompiladorParser(tokens)
    parser.removeErrorListeners()
    parser.addErrorListener(CustomErrorListener())

    try:
        tree = parser.inicio()
        validate_security(input_stream.strdata)
        
        # Ejemplo de uso del evaluador optimizado
        optimized_eval_visitor = OptimizedEvalVisitor()
        result = optimized_eval_visitor.visitInicio(tree)
        
        # Imprimimos el resultado
        print("Resultado optimizado:", result)
        
        # Usamos un listener para imprimir eventos de entrada y salida de nodos
        listener = MiCompiladorListenerImpl()
        walker = ParseTreeWalker()
        walker.walk(listener, tree)
    except ValueError as ve:
        print(f"Error: {ve}")
    except SecurityError as se:
        print(f"Error de seguridad: {se}")

if __name__ == '__main__':
    main()
