"""
Módulo para la detección, validación y normalización de expresiones horarias.
Autor: Guillem Pérez Sánchez
QP 2026
"""

import re


def normalizaHoras(ficText, ficNorm):
    """
    Lee el fichero 'ficText', busca expresiones horarias de diversas formas
    en castellano, las valida lógicamente y escribe en 'ficNorm' el texto con 
    las horas normalizadas al formato estándar 'HH:MM'.
    """

    def procesar_coincidencia(match):
        """
        Función auxiliar interna que procesa los tokens de la expresión regular,
        valida las restricciones horarias semánticas y devuelve la hora
        formateada en formato 24h o la cadena original si es inválida.
        """
        texto_original = match.group(0)
        hora_str = match.group(1)
        
        # Identificación de minutos numéricos o cadenas de texto específicas
        minuto_str = match.group(2) if match.group(2) else match.group(3)
        modificador = match.group(4)
        
        # Búsqueda secundaria para aislar la franja horaria literal
        franja_match = re.search(
            r'(mañana|mediodía|tarde|noche|madrugada)', 
            texto_original, 
            re.IGNORECASE
        )
        franja = franja_match.group(1).lower() if franja_match else None

        # Descarte de falsos positivos: Números descontextualizados (ej: "7 puertas")
        if not minuto_str and not modificador and not franja and 'h' not in texto_original.lower():
            return texto_original

        h = int(hora_str)
        m = 0

        # 1. Validación de la consistencia en el formato de los minutos
        if minuto_str:
            if 'cuarto' in minuto_str:
                m = 15
            elif 'media' in minuto_str:
                m = 30
            else:
                m_limpio = re.sub(r'[^\d]', '', minuto_str)
                if m_limpio:
                    # Si tiene un solo dígito sin cero a la izquierda ni 'm' ("17:5") es incorrecto
                    if len(m_limpio) == 1 and not minuto_str.startswith('0') and 'm' not in minuto_str:
                        return texto_original
                    m = int(m_limpio)

        # 2. Modificaciones relativas ("menos cuarto")
        if modificador and 'menos' in modificador:
            h -= 1
            m = 45

        # 3. Conversión analógica/digital y comprobación estricta de franjas
        if franja:
            # Una franja explícita obliga al uso de un formato de 12 horas (rango 1-12)
            if h < 1 or h > 12:
                return texto_original
            
            if 'mañana' in franja:
                if h < 4 or h > 12: return texto_original
                h_24 = 12 if h == 12 else h
            elif 'mediodía' in franja:
                if h != 12 and h > 3: return texto_original
                h_24 = 12 if h == 12 else h + 12
            elif 'tarde' in franja:
                if h < 3 or h > 8: return texto_original
                h_24 = 12 if h == 12 else h + 12
            elif 'noche' in franja:
                if h < 8 and h > 4: return texto_original
                if h == 12: h_24 = 0
                elif 1 <= h <= 4: h_24 = h
                else: h_24 = h + 12
            elif 'madrugada' in franja:
                if h < 1 or h > 6: return texto_original
                h_24 = 0 if h == 12 else h
        else:
            # Sin franja explícita en el texto
            if modificador and ('punto' in modificador or 'cuarto' in modificador or 'media' in modificador):
                # Las expresiones coloquiales ("8 en punto") se mapean de 00:00 a 11:59 por defecto
                if h < 1 or h > 12:
                    return texto_original
                h_24 = 0 if h == 12 else h
            else:
                # Formato digital clásico (24h). Ejemplo: 18:30, 23h, 17h5m
                if h < 0 or h > 23:
                    return texto_original
                h_24 = h

        # Restricción final matemática sobre el rango de los minutos
        if m < 0 or m > 59:
            return texto_original

        return f"{h_24:02d}:{m:02d}"

    # --- Lógica de procesamiento de ficheros ---
    
    # Patrón RegEx que encapsula todas las ramificaciones gramaticales del enunciado
    patron_horas = re.compile(
        r'\b(\d{1,2})'
        r'(?:(?:[:hH](\d{1,2})m?)|(?:\s+(y\s+cuarto|y\s+media)))?'
        r'(?:\s+(en\s+punto|menos\s+cuarto))?'
        r'(?:\s+de\s+la\s+(?:mañana|tarde|noche|madrugada)|'
        r'\s+del\s+mediodía)?'
    )

    with open(ficText, 'r', encoding='utf-8') as f_in, \
         open(ficNorm, 'w', encoding='utf-8') as f_out:
        
        for linea in f_in:
            pos = 0
            linea_procesada = ""
            
            # Buscar concordancias de manera secuencial dentro de cada línea
            for match in patron_horas.finditer(linea):
                linea_procesada += linea[pos:match.start()]
                linea_procesada += procesar_coincidencia(match)
                pos = match.end()
            
            linea_procesada += linea[pos:]
            f_out.write(linea_procesada)
