from dokk.cli import main

# Guarded: worker processes for parallel builds re-import the main module.
if __name__ == "__main__":
    raise SystemExit(main())
