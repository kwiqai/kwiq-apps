# import core
from kwiq.core.app import App

from smart_code_merge.setup import Setup
from smart_code_merge.apply_transformation import ApplyTransformation
from smart_code_merge.prepare_transformation import PrepareTransformation
from smart_code_merge.merge import Merge
from smart_code_merge.commit import Commit


def main():
    app = App(name="smart-code-merge")
    app.register_flow(Setup())
    app.register_flow(PrepareTransformation())
    app.register_flow(ApplyTransformation())
    app.register_flow(Merge())
    app.register_flow(Commit())

    app.main()


if __name__ == '__main__':
    main()
