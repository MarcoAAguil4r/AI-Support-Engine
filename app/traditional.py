import re

from app.schemas import AnalyzeResponse, Category, Mode, Priority


RULES: tuple[tuple[Category, tuple[str, ...]], ...] = (
    (
        Category.SECURITY,
        (
            r"\bseguridad\b",
            r"\bvulnerabil\w*",
            r"\bexploit\b",
            r"\bcve-\d{4}-\d+\b",
            r"\bmalware\b",
            r"\bransomware\b",
            r"\b(phishing|filtraci[oó]n|exposici[oó]n de datos)\b",
            r"\b(acceso no autorizado|cuenta comprometida|robo de datos)\b",
            r"\b(hacke\w*|breach|injection|inyecci[oó]n)\b",
        ),
    ),
    (
        Category.ACCESS,
        (
            r"\b(iniciar sesi[oó]n|inicio de sesi[oó]n|login|sign in|log in)\b",
            r"\b(acceso|acceder|entrar|contrase[nñ]a|password|autenticaci[oó]n)\b",
            r"\b(cuenta|bloquead[ao]|restablecer)\b",
        ),
    ),
    (
        Category.BUG,
        (
            r"\b(error|bug|falla|fallo|defecto|crash|excepci[oó]n)\b",
            r"\b(no funciona|deja de funcionar|se cierra|pantalla en blanco)\b",
            r"\b(lento|ca[ií]do|indisponible|timeout)\b",
        ),
    ),
    (
        Category.FEATURE,
        (
            r"\b(nueva funci[oó]n|funcionalidad|caracter[ií]stica|feature)\b",
            r"\b(me gustar[ií]a|quisiera|solicito|solicitud|sugerencia)\b",
            r"\b(agregar|a[nñ]adir|implementar|incorporar)\b",
        ),
    ),
)

CRITICAL_SIGNALS = (
    r"\b(producci[oó]n|todos los usuarios|toda la empresa)\b",
    r"\b(exfiltraci[oó]n|datos expuestos|datos robados|ransomware)\b",
    r"\b(urgente|inmediato|en curso|activo)\b",
)
HIGH_SIGNALS = (
    r"\b(m[oó]ltiples usuarios|varios usuarios|equipo completo)\b",
    r"\b(impacto alto|bloquea|bloquead[ao]s?|no disponible|no pueden trabajar)\b",
)

DEFAULT_RESPONSES = {
    Category.ACCESS: (
        "Lamentamos el inconveniente. Verifique sus credenciales y utilice "
        "la recuperación de contraseña si es necesario."
    ),
    Category.BUG: (
        "Gracias por reportar la falla. Registramos el problema para que el "
        "equipo técnico pueda reproducirlo e investigarlo."
    ),
    Category.FEATURE: (
        "Gracias por la sugerencia. La registramos para que el equipo de "
        "producto evalúe su alcance y prioridad."
    ),
    Category.SECURITY: (
        "Gracias por alertarnos. El reporte se derivará de forma prioritaria "
        "al equipo de seguridad; no comparta datos sensibles por este canal."
    ),
}


def _matches_any(message: str, patterns: tuple[str, ...]) -> bool:
    return any(re.search(pattern, message, re.IGNORECASE) for pattern in patterns)


def has_security_indicators(message: str) -> bool:
    return _matches_any(message, RULES[0][1])


def classify(message: str) -> tuple[Category, Priority]:
    category = next(
        (
            candidate
            for candidate, patterns in RULES
            if _matches_any(message, patterns)
        ),
        Category.BUG,
    )

    if category == Category.SECURITY:
        if _matches_any(message, CRITICAL_SIGNALS):
            return category, Priority.CRITICAL
        return category, Priority.HIGH

    if _matches_any(message, CRITICAL_SIGNALS):
        return category, Priority.CRITICAL
    if _matches_any(message, HIGH_SIGNALS):
        return category, Priority.HIGH
    if category == Category.FEATURE:
        return category, Priority.LOW
    if category == Category.BUG and _matches_any(message, (r"\bmenor\b", r"\bvisual\b")):
        return category, Priority.LOW
    return category, Priority.MEDIUM


def analyze_traditionally(message: str) -> AnalyzeResponse:
    category, priority = classify(message)
    return AnalyzeResponse(
        category=category,
        priority=priority,
        response=DEFAULT_RESPONSES[category],
        requiresHumanReview=category == Category.SECURITY,
        mode=Mode.traditional,
    )
