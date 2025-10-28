import Programmi.functions_revolver as functions_revolver

s1 = r'""[2025, 2024]"'
s2 = r"'prova"
s3 = r'"prova'
s4 = r'prova"'
s5 = r"'prova"
s6 = r"prova'"

s7 = r"pro'va"
s8 = r'pro"va'

s9 = r"''prova"
s10 = r"prova''"
s11 = r'""prova'
s12 = r"prova'''"
s13 = r'""prova"'

print( functions_revolver.clean_field( s1 ) )
print( functions_revolver.clean_field( s2 ) )
print( functions_revolver.clean_field( s3 ) )
print( functions_revolver.clean_field( s4 ) )
print( functions_revolver.clean_field( s5 ) )
print( functions_revolver.clean_field( s6 ) )
print( functions_revolver.clean_field( s7 ) )
print( functions_revolver.clean_field( s8 ) )
print( functions_revolver.clean_field( s9 ) )
print( functions_revolver.clean_field( s10 ) )
print( functions_revolver.clean_field( s11 ) )
print( functions_revolver.clean_field( s12 ) )
print( functions_revolver.clean_field( s13 ) )

