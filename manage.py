#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys


def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Django não foi encontrado. "
            "Verifique se as dependências estão instaladas "
            "e se o ambiente virtual está ativo."
        ) from exc
    except Exception as e:
        print(f"Erro inesperado ao carregar Django: {e}")
        sys.exit(1)

    try:
        execute_from_command_line(sys.argv)
    except Exception as e:
        print(f"Erro ao executar comando: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()