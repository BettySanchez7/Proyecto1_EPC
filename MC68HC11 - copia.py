from LeerArchivos import *
from string import hexdigits
from tkinter import *
from tkinter.filedialog import *
###El fist_espace es el que determina como leer el archivo, es decir que lineas tomar o no para el analisis, las que 
#no tienen espacio al principio no las lee ya que solo son nombres de etiquetas, constantes o comentario, variables, etc.
class Program(object):
    #define variable a usar, metodos
    def __init__(self,name):
        self.iniciar_memoria = '0'
        self.name = name
        self.var = {}
        self.memoria = []
        self.mem_posicion = 0
        self.posicion_linea = 0
        self.etiqueta = {}
        self.started = False
        self.finished = False
        self.errores = 0
        self.jmp_etiqueta = {}
        self.bullet = self.iniciar_memoria
        self.num_bullet = 0
        self.codigoob = {}
        self.codigoob2 = {} #######
        self.lineas_totales = 0
        self.org_memoria = []
        self.num_codigo = 0

class Errores(BaseException):                                   #Calculando cuantos errores hay en el programa
    def __init__(self,codigo,error_linea,op_name = ''):
        self.codigo = codigo
        self.error_linea = str(error_linea)                     #La palabra que este mal se guardará en un a cadena
        self.op_name = op_name
        programa.errores +=1




def set_bullet(item):
    memoria = int(programa.bullet, 16)
    if item == 8:
        auxiliar = 4
    elif item == 6:
        auxiliar = 3
    elif item == 4:
        auxiliar = 2
    else:
        auxiliar = 1
    memoria += int(auxiliar)
    programa.bullet = hex(memoria)[2::].upper()


def lexer(linea):
    linea = linea.split()                                       #split separa las palabras que encuentra en una linea
    for item in linea:
        if '*' in item:
            for x in range(len(linea)-1,linea.index(item)-1,-1): #recorre la linea en un intervalo de inicio hasta el comentario
                linea.pop(x)                                     #pop() Devuelve el ultimo valor de la linea
    return linea                                               #regresa la linea sin los comentarios

def lexer2(linea):########################
    linea = linea.split()                                       #split separa las palabras que encuentra en una linea
    for item in linea:
        if '*' in item:
            for x in range(linea.index(item)-1,len(linea)-1,1): #recorre la linea en un intervalo de inicio hasta el comentario
                linea.pop(x)                                     #pop() Devuelve el ultimo valor de la linea
    return lineas_totales           #Quiero que devuleva los comentarios de cada linea

def limpiar_valor(valor):                                        #quita caracteres que no se deben mostrar en el lst
    valor = valor.replace('#','')                                #.replace() sustituye la variable encontrada por nada
    valor = valor.replace('$','')
    valor = valor.replace(',X','')
    valor = valor.replace(',Y','')
    valor = valor.replace(',','')
    if valor not in programa.var and valor not in programa.etiqueta and valor not in programa.jmp_etiqueta:
        is_valor_hex = True
        for letter in valor:
            if letter not in hexdigits:
                is_valor_hex = False

        if is_valor_hex:
            if len(valor)==3 or len(valor)==1:                  # para palabras de 4 bytes
                while len(valor)!=4:
                    valor = '0'+valor
    return valor

def saltoRelativo(a,b):                                        #hace saltos valuesRELs
    salto = a - b - 2
    if abs(salto)>127:
        raise Errores(2,programa.lineas_totales)
    if salto<0:
        salto = int(bin(salto)[3::],2) - (1 << 8)
    salto = hex(salto)[3 if salto < 0 else 2::].upper()
    while len(salto)<2:
        salto = '0'+salto
    return salto

def format_linea(lista,firstspace):                              #aquí se ajustan los colores de la impresión
    if len(lista)==3 and first_space:                            
        flinea = ''.ljust(9)+lista[0].ljust(8)+lista[1].ljust(15)+lista[2]
    elif len(lista) == 3:
        flinea = lista[0].ljust(9)+lista[1].ljust(8)+lista[2]
    elif len(lista) == 2 and first_space:
        flinea = ''.ljust(9)+lista[0].ljust(8)+lista[1]
    elif len(lista) == 2:
        flinea = lista[0].ljust(9)+lista[1]
    elif first_space:
        flinea = ''.ljust(9)+lista[0]
    else:
        flinea = lista[0]
    return flinea

def verify_length(valor,byts):                                    #lanza el error si el operando es erroneo, no hay congruencia en etiquetas y/o constantes
    if len(valor) != byts*2:
        raise Errores(1,programa.lineas_totales)
    elif not valor.isnumeric() and (valor not in programa.etiqueta or valor not in programa.var):
        raise Errores(6 if valor not in programa.var else 4,programa.lineas_totales)


def check_etiqueta(tag):                                         #verifica etiquetas
    if tag != "no_tag" and tag not in programa.etiqueta:
        programa.etiqueta.update({tag:programa.mem_posicion})    #agrega el valor de la etiqueta
    programa.mem_posicion += int(len(programa.memoria[-1])/2)

def INICIO(iniciar_memoria_define,tag,op_name):                   # valor que toma ORG en memoria
    if not programa.started:
        programa.iniciar_memoria = limpiar_valor(iniciar_memoria_define)
        programa.mem_posicion = int(programa.iniciar_memoria,16)
        programa.started = True
    verify_length(programa.iniciar_memoria, 2)
    auxiliar = int(limpiar_valor(iniciar_memoria_define), 16)
    programa.org_memoria.append(hex(auxiliar).upper()[2::])
    programa.memoria.append(hex(auxiliar).upper()[2::])



def LDX(valor,tag,op_name):                                       #modos de direccionamiento
    if limpiar_valor(valor) in programa.var:                      #extendido
        if '#' in valor:
            programa.memoria.append(valuesIMM[op_name]+programa.var[limpiar_valor(valor)])
        elif len(programa.var[limpiar_valor(valor)])==2 and op_name in valuesDIR:                  #elif= else if
            programa.memoria.append(valuesDIR[op_name]+programa.var[limpiar_valor(valor)])
        elif len(programa.var[limpiar_valor(valor)])==4:
            programa.memoria.append(valuesEXT[op_name]+programa.var[limpiar_valor(valor)])
        else:
            programa.memoria.append(valuesEXT[op_name]+programa.var[limpiar_valor(valor)]) #OPTIMIZACIÓN DE CÓDIGO
    elif '#' in valor:                                            #valuesIMM
        valor = limpiar_valor(valor)
        if '\'' in valor:
            programa.memoria.append(valuesIMM[op_name]+hex(ord(valor.replace('\'','')))[2::].upper())
        elif len(valor) == 2 or len(valor) == 4:
            programa.memoria.append(valuesIMM[op_name]+valor)
        else:
            raise Errores(1,programa.lineas_totales)
    elif ',' in valor:                                            #INDEXADO
        if 'X' in valor:#X
            valor = limpiar_valor(valor)
            verify_length(valor, 1)
            programa.memoria.append(valuesINDX[op_name]+valor)
        elif 'Y' in valor:#Y
            valor = limpiar_valor(valor)
            verify_length(valor, 1)
            programa.memoria.append(valuesINDY[op_name]+valor)
        else:
            raise Errores(7,programa.lineas_totales)
    elif '$' in valor:                                            #DIRECTO O EXTENDIDO
        valor = limpiar_valor(valor)
        if len(valor) == 2:
            programa.memoria.append(valuesDIR[op_name]+valor.replace('$',''))
        elif len(valor) == 4:
            programa.memoria.append(valuesEXT[op_name]+valor.replace('$',''))
        else:
            raise Errores(1,programa.lineas_totales)
    elif valor == "no_valor":
        raise Errores(7,programa.lineas_totales)
       
    check_etiqueta(tag)                                           #etiquetas

#mnemonicos especiales y directivas
def EQU(valor,name,op_name):
    if int(valor.replace('$',''),16)<=int('FF',16):
        valor = valor[3:]
    programa.var.update({name:valor.replace('$','')})             #agregamos el valor a nombre en el diccionario
    programa.memoria.append(valor.replace('$',''))                #con append se agrega el valor a la lista


def NOP(valor, tag,op_name):
    if valor != "no_valor":
        raise Errores(8,programa.lineas_totales)
    programa.memoria.append(valuesINH[op_name])
    check_etiqueta(tag)

def BRCLR(valor,tag,op_name):
    mnem_extra = 0
    if 'X' in valor or 'Y' in valor:
        if 'X' in valor:
            valor = especiales[op_name][1]+limpiar_valor(valor)
        else:
            valor = especiales[op_name][2]+limpiar_valor(valor)
    else:
        valor = especiales[op_name][0]+limpiar_valor(valor)
    programa.memoria.append(valor)                               #agregamos el valor de BRCLR a la lista 
    programa.mem_posicion += int(len(programa.memoria[-1])/2)
    if tag in programa.etiqueta:
        programa.memoria[-1]=programa.memoria[-1]+saltoRelativo(programa.etiqueta[tag],programa.mem_posicion-1)
        mnem_extra += 1
    elif tag in programa.jmp_etiqueta:
        programa.jmp_etiqueta.update({tag:[valor,programa.lineas_totales,programa.jmp_etiqueta[valor][2]+1,programa.mem_posicion,op_name]})
        programa.memoria[-1] = tag
        mnem_extra += 1
    elif tag != "no_tag":
        programa.jmp_etiqueta.update({tag:[valor,programa.lineas_totales,1,programa.mem_posicion,op_name]})
        programa.memoria[-1] = tag
    programa.mem_posicion += mnem_extra

def BNE(valor,tag,op_name):
    if valor == "no_valor":
        valor = tag
    if valor in programa.etiqueta:
        programa.memoria.append(valuesREL[op_name]+saltoRelativo(programa.etiqueta[tag],programa.mem_posicion))
    elif valor in programa.jmp_etiqueta:
        programa.jmp_etiqueta.update({valor:[valuesREL[op_name],programa.lineas_totales,programa.jmp_etiqueta[valor][2]+1,programa.mem_posicion+2]})
        programa.memoria.append(valor)
    else:
        programa.jmp_etiqueta.update({valor:[valuesREL[op_name],programa.lineas_totales,1,programa.mem_posicion]})
        programa.memoria.append(valor)
    programa.mem_posicion+=2
    if tag != "no_tag" and tag not in programa.etiqueta:
        programa.etiqueta.update({tag:programa.mem_posicion})


def FCB(valor1):
    programa.memoria.append(limpiar_valor(valor1)+' ')

def JMP(valor,tag,op_name):
    if valor == "no_valor":
        valor = tag
    if valor in programa.jmp_etiqueta:
        programa.jmp_etiqueta.update({valor:[valuesEXT[op_name],programa.lineas_totales,programa.jmp_etiqueta[valor][2]+1]})
        programa.memoria.append(valor)
        programa.mem_posicion += 3
    elif valor in programa.etiqueta:
        programa.memoria.append(valuesEXT[op_name]+hex(programa.etiqueta[tag]).upper()[2::])
        programa.mem_posicion += 3
    elif limpiar_valor(valor).isnumeric() or limpiar_valor(valor) in programa.var:
        if (len(limpiar_valor(valor)) != 2 or len(limpiar_valor(valor)) != 4) and limpiar_valor(valor) not in programa.var:
            raise Errores(1,programa.lineas_totales)
        if ',X' in valor:
            programa.memoria.append(indiceadox[op_name]+limpiar_valor(valor))
            programa.mem_posicion += 2
        elif ',Y' in valor:
            programa.memoria.append(indiceadoy[op_name]+limpiar_valor(valor))
            programa.mem_posicion += 3
        elif len(limpiar_valor(valor)) == 2:
            programa.memoria.append(valuesDIR[op_name]+limpiar_valor(valor))
            programa.mem_posicion += 2
        else:
            valor = programa.var[valor]
            while len(valor) < 4:
                valor = '0'+valor
            programa.memoria.append(valuesEXT[op_name]+valor)
            programa.mem_posicion += 3
    else:
        programa.jmp_etiqueta.update({valor:[valuesEXT[op_name],programa.lineas_totales,1]})
        programa.memoria.append(valor)
        programa.mem_posicion += 3

def END(valor,tag,op_name):
    programa.finished = True
    programa.codigoob.update({programa.lineas_totales:op_name.ljust(8)+(valor if valor != 'no_valor' else '')})
#asociados a los de arriba
mnemonico={'ABA':NOP,'ABX':NOP,'ABY':NOP,'ADCA':LDX,'ADCB':LDX,'ADDA':LDX,'ADDB':LDX,'ADDD':LDX,'ANDA':LDX,'ANDB':LDX,'ASL':LDX,'ASLA':NOP,'ASLB':NOP,'ASLD':NOP,'ASR':LDX,'ASRA':NOP,'ASRB':NOP,'BCC':BNE,'BCLR':BRCLR,'BCS':BNE,'BEQ':BNE,'BGE':BNE,'BGT':BNE,'BHI':BNE,'BHS':BNE,'BITA':LDX,'BITB':LDX,'BLE':BNE,'BLO':BNE,'BLS':BNE,'BLT':BNE,'BMI':BNE,'BNE':BNE,'BPL':BNE,'BRA':BNE,'BRCLR':BRCLR,'BRN':BNE,'BRSET':BRCLR,'BSET':BRCLR,'BSR':BNE,'BVC':BNE,'BVS':BNE,'CBA':NOP,'CLC':NOP,'CLI':NOP,'CLR':LDX,'CLRA':NOP,'CLRB':NOP,'CLV':NOP,'CMPA':LDX,'CMPB':LDX,'COM':LDX,'COMA':NOP,'COMB':NOP,'CPD':LDX,'CPX':LDX,'CPY':LDX,'DAA':NOP,'DEC':LDX,'DECA':NOP,'DECB':NOP,'DES':NOP,'DEX':NOP,'DEY':NOP,'END':END,'EORA':LDX,'EORB':LDX,'EQU':EQU,'FCB':FCB,'FDIV':NOP,'IDIV':NOP,'INC':LDX,'INCA':NOP,'INCB':NOP,'INS':NOP,'INX':NOP,'INY':NOP,'JMP':JMP,'JSR':JMP,'LDAA':LDX,'LDAB':LDX,'LDD':LDX,'LDS':LDX,'LDX':LDX,'LDY':LDX,'LSL':LDX,'LSLA':NOP,'LSLB':NOP,'LSLD':NOP,'LSR':LDX,'LSRA':NOP,'LSRB':NOP,'LSRD':NOP,'MUL':NOP,'NEG':LDX,'NEGA':NOP,'NEGB':LDX,'NOP':NOP,'ORAA':LDX,'ORAB':LDX,'ORG':INICIO,'PSHA':NOP,'PSHB':NOP,'PSHX':NOP,'PSHY':NOP,'PULA':NOP,'PULB':NOP,'PULX':NOP,'PULY':NOP,'ROL':LDX,'ROLA':NOP,'ROLB':NOP,'ROR':LDX,'RORA':NOP,'RORB':NOP,'RTI':NOP,'RTS':NOP,'SBA':NOP,'SBCA':LDX,'SBCB':LDX,'SEC':NOP,'SEI':NOP,'SEV':NOP,'STAA':LDX,'STAB':LDX,'STD':LDX,'STOP':NOP,'STS':LDX,'STX':LDX,'STY':LDX,'SUBA':LDX,'SUBB':LDX,'SUBD':LDX,'SWI':NOP,'TAB':NOP,'TAP':NOP,'TBA':NOP,'TETS':NOP,'TPA':NOP,'TST':LDX,'TSTA':NOP,'TSTB':NOP,'TSX':NOP,'TSY':NOP,'TXS':NOP,'TYS':NOP,'WAI':NOP,'XGDX':NOP,'XGDY':NOP}

#programa = Program(input('introduce tu Archivo con la extensión .asc): '))

def compilauno():
   
   return entrada.get()

ventana=Tk()
entrada=StringVar()
welcome= Label(ventana,text=" BIENVENIDO AL COMPILADOR DEL MC68HC11 ",font=("Agency FB",14)).place(x=30,y=20)
Etiqueta= Label(ventana,text="1.-Ingrese el nombre del archivo a compilar(extensión *.asc)\n2.-Presione el boton Complilar\n3.-Finalmente cierre la ventana.",font=("Agency FB",10)).place(x=0,y=70)
Caja=Entry(ventana,textvariable=entrada).place(x=250,y=150)
ventana.title('COMPILADOR MC68HC11')
ventana.geometry("500x300")
botonCompila=Button(ventana,text="Compilar",font=("Agency FB",10),command=compilauno)  
botonCompila.grid(padx=50,pady=150)
ventana.mainloop()
programa=1
programa=Program(compilauno())

try:
    file = open(programa.name,"r")
    f = open(programa.name.replace('.ASC','.lst'), "w")
    h = open(programa.name.replace('.ASC','.hex'), "w")
except:
    print('\tERROR 404 ARCHIVO NOT FOUND, NO SE ENCONTRO EL ARCHIVO, ¡HASTA LUEGO!')
    exit(-1)





#leer archivo linea por linea

for linea in file:
    first_space = True if linea[0] == ' ' or linea[0] == '\t' else False  
    lineabase=linea #####
    linea = lexer(linea)

  
    programa.lineas_totales+=1

    if len(linea)>0:
        programa.posicion_linea+=1
        programa.codigoob.update({programa.posicion_linea:format_linea(linea,first_space)})  ##########linea2 por linea1
      
    try:
        if len(linea)>=2:
            if linea[0] in especiales or linea[1] in especiales:
                if linea[0] in mnemonico:
                    mnemonico[linea[0]](linea[1],linea[2] if len(linea) == 3 else "no_tag",linea[0])
                else:
                    raise Errores(3,programa.lineas_totales,linea[0] if linea[0] in especiales else linea[1])
                linea = ''
          

        if len(linea) == 3:
            if linea[1] not in mnemonico:
                raise Errores(3,programa.lineas_totales,linea[1])
         
            if linea[1] == 'FCB':
                mnemonico[linea[1]](linea[2])
            else:
                mnemonico[linea[1]](linea[2], linea[0],linea[1])
        elif len(linea) == 2:
            if linea[0] in mnemonico:
                if linea[1] in programa.etiqueta:
                    mnemonico[linea[0]]("no_valor", linea[1],linea[0])
                elif linea[0] == 'FCB':
                    mnemonico[linea[0]](linea[1])
                else:
                    mnemonico[linea[0]](linea[1], "no_tag",linea[0])
            elif linea[1] in mnemonico:
                mnemonico[linea[1]]("no_valor", linea[0],linea[1])
            else:
                raise Errores(3,programa.lineas_totales,linea[0])
        elif len(linea) == 1:
            if linea[0] in mnemonico and first_space:
                mnemonico[linea[0]]("no_valor", "no_tag",linea[0])
            elif not first_space:
                programa.etiqueta.update({linea[0]:programa.mem_posicion})
            else:
                raise Errores(3,programa.lineas_totales,linea[0])
    #errores
    except KeyError:
        print("ERROR 007 MAGNITUD DE OPERANDO ERRONEA"+str(programa.lineas_totales)+' K')
    except Errores as e:
        if e.codigo == 1:
            print("ERROR 007 MAGNITUD DE OPERANDO ERRONEA "+e.error_linea)
        elif e.codigo == 2:
            print("ERROR 008 SALTO RELATIVO MUY LEJANO"+e.error_linea)
        elif e.codigo == 3:
            print("ERROR 004 MNEMÓNICO"+e.op_name+"\tINEXISTENTE EN LINEA"+e.error_linea)
        elif e.codigo == 4:
            print("ERROR 003 ETIQUETA "+e.op_name+"\tINEXISTENTE EN LINEA"+e.error_linea)
        elif e.codigo == 5:
            print("ERROR 002 VARIABLE "+e.op_name+"INEXISTENTE "+e.error_linea)
        elif e.codigo == 6:
            print("ERROR 001 CONSTANTE"+e.op_name+"INEXISTENTE EN LINEA "+e.error_linea)
        elif e.codigo == 7:
            print("ERROR 005 INSTRUCCIÓN CARECE DE OPERANDO(S)"+e.error_linea)
        elif e.codigo == 8:
            print("ERROR 006 INSTRUCCIÓN NO LLEVA OPERANDO(S)"+e.error_linea)
  
#etiquetas salto relativo
for indice,entry in enumerate(programa.memoria):
    if entry in programa.jmp_etiqueta and entry in programa.etiqueta:
        if programa.jmp_etiqueta[entry][0] in valuesREL.values() or len(programa.jmp_etiqueta[entry]) == 5:
            try:
                programa.memoria[indice]= str(programa.jmp_etiqueta[entry][0])+saltoRelativo(programa.etiqueta[entry],programa.jmp_etiqueta[entry][3])
            except Errores as e:
                print("ERROR 008 SALTO RELATIVO MUY LEJANO"+str(programa.jmp_etiqueta[entry][1]))
        else:
            programa.memoria[indice]= str(programa.jmp_etiqueta[entry][0])+hex(programa.etiqueta[entry])[2::].upper()
        programa.jmp_etiqueta[entry][2]+=-1
for key in programa.jmp_etiqueta:
    if programa.jmp_etiqueta[key][2]>0:
        print("ERROR 003 ETIQUETA"+key+"\tINEXISTENTE EN LINEA"+str(programa.jmp_etiqueta[key][1]))
        programa.errores += 1
        if programa.memoria.count(key)>1:
            print("\tETIQUETA INEXISTENTE PRESENTE"+str(programa.memoria.count(key))+" veces")
#error 9
if not programa.finished:
    programa.errores += 1
    print("ERROR 010 NO SE ENCUENTRA END")
print('\n\t\tTotal de líneas de código:'+str(programa.lineas_totales)+'\n\t\tNumero de errores '+str(programa.errores))
if programa.errores > 0:
    exit(1)

'''Se compiló el programa en número de línea y el codigo objeto'''
pass_var = False
aumentar_espacios=1


try:
    for indice,item in enumerate(programa.memoria):
        indice+=aumentar_espacios
        if item in programa.org_memoria:               #obtenemos una lista de tuplas con método item
        ###formato de c
            f.write(str(indice).ljust(4)+':'.ljust(8)+item.ljust(12)+':'+programa.codigoob[indice]+'\n')
            programa.bullet = item
        else:
            if item in programa.var.values() and programa.bullet == '0':
                f.write(str(indice).ljust(4)+':'.ljust(8)+item.zfill(4)+':'.rjust(9)+programa.codigoob[indice]+'\n')
            elif (programa.codigoob[indice][0]!=' ' and programa.codigoob[indice][0]!='\t') and len(lexer(programa.codigoob[indice])) == 1:
                while (programa.codigoob[indice][0]!=' ' and programa.codigoob[indice][0]!='\t') and len(lexer(programa.codigoob[indice])) == 1:
                    f.write(str(indice).ljust(4)+':'+programa.bullet.ljust(7)+''.ljust(12)+':'+programa.codigoob[indice]+'\n')  #ETIQUETAS
                    indice+=1
                    aumentar_espacios+=1
                if(len(item)==2):
                    f.write(str(indice).ljust(4)+':'+programa.bullet.ljust(7)+'('+item+')'.ljust(9)+':'+programa.codigoob[indice]+'\n')
                    set_bullet(len(item))
                elif(len(item)==4):
                    f.write(str(indice).ljust(4)+':'+programa.bullet.ljust(7)+'('+item+')'.ljust(7)+':'+programa.codigoob[indice]+'\n')
                    set_bullet(len(item))
                elif(len(item)==8):
                    f.write(str(indice).ljust(4)+':'+programa.bullet.ljust(7)+'('+item+')'.ljust(3)+':'+programa.codigoob[indice]+'\n')
                    set_bullet(len(item))

                else:
                    f.write(str(indice).ljust(4)+':'+programa.bullet.ljust(7)+'('+item+')'.ljust(5)+':'+programa.codigoob[indice]+'\n')
                    set_bullet(len(item))
            else:
                if(len(item)==2):
                    f.write(str(indice).ljust(4)+':'+programa.bullet.ljust(7)+'('+item+')'.ljust(9)+':'+programa.codigoob[indice]+'\n')
                    set_bullet(len(item))
                elif(len(item)==4):
                    f.write(str(indice).ljust(4)+':'+programa.bullet.ljust(7)+'('+item+')'.ljust(7)+':'+programa.codigoob[indice]+'\n')
                    set_bullet(len(item))
                elif(len(item)==8):
                    f.write(str(indice).ljust(4)+':'+programa.bullet.ljust(7)+'('+item+')'.ljust(3)+':'+programa.codigoob[indice]+'\n')
                    set_bullet(len(item))
                else:
                    f.write(str(indice).ljust(4)+':'+programa.bullet.ljust(7)+'('+item+')'.ljust(5)+':'+programa.codigoob[indice]+'\n')
                    set_bullet(len(item))
    indice+=1
    while indice< len(programa.codigoob) and 'END' not in lexer(programa.codigoob[indice-1]):
        if programa.codigoob[indice][0]!=' ' and programa.codigoob[indice][0]!='\t':
          f.write(str(indice).ljust(4)+':'+programa.bullet.ljust(7)+item.ljust(12)+':'+programa.codigoob[indice]+'\n')
        else:
            f.write(str(indice).ljust(4)+':'+programa.bullet.ljust(7)+''.ljust(12)+':'+programa.codigoob[indice]+'\n')
        indice+=1
#dice el error y en la linea de codigo
except KeyError:
    print('Keyerror in linea'+str(indice)+item+programa.codigoob[indice-1])
#para tabla de simbolos
symbol_table = programa.etiqueta.copy()
symbol_table.update(programa.var)
symbol_table.update(programa.jmp_etiqueta)
f.write('\nTabla de Simbolos, total: '+str(len(symbol_table))+'\n')
for key in sorted(symbol_table):
    if key in programa.etiqueta:
        f.write(key+'\t'+hex(programa.etiqueta[key])[2:].upper()+'\n')
    elif key in programa.jmp_etiqueta:
        f.write(key+'\t'+hex(programa.jmp_etiqueta[key])[2:].upper()+'\n')
    else:
        f.write(key+'\t'+('' if len(programa.var[key])==4 else '00' )+programa.var[key]+'\n')

bullet = 0
posicion = 1
for item in programa.memoria:
    if item in programa.org_memoria:
        posicion = 1
        bullet = item
        h.write(('\n' if bullet != programa.org_memoria[0] else '<')+bullet+'> ')
    elif bullet != 0:
        while posicion<=16 and item != '':
            h.write(item[:2]+' ')
            item = item.replace(item[:2],'')
            posicion += 1
        if posicion > 16:
            posicion = 1
            bullet = str(hex(int(bullet,16)+16)[2:].upper()) #uppSer retorna la cadena en mayusculas en este caso el hexa
            h.write('\n<'+bullet+'> ')
            while item != '':
                h.write(item[:2]+' ')
                item = item.replace(item[:2],'')
                posicion += 1


#print(programa.codigoob)
f.close()
h.close()
file.close()
print('Archivo lst ' +programa.name.replace('.ASC','.lst')+' creado correctamente')  #Genera el archivo .ls reempazando la extensión
print('Archivo hex ' +programa.name.replace('.ASC','.hex')+' creado correctamente')  #Genera el archivo .hex reemplazando la extensión
