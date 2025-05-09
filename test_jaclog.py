from jaclog import *
import pytest

def test_basic_operations(capsys):
    db = Database()
    db.add_callmap({"print": print})

    result = True

    result = result and AssertStatement(db, "lokacja_gracza", ["Izba"]).run()
    result = result and AssertStatement(db, "lokacja_postaci", ["Pan Młody", "Izba"]).run()
    result = result and RetractStatement(db, "lokacja_gracza", ["Izba"]).run()
    result = result and RunStatement(db, "lokacja_postaci", ["Pan Młody", "Izba"]).run()
    result = result and not RunStatement(db, "lokacja_gracza", ["Izba"]).run()

    assert result


def test_rules_definitions(capsys):
    db = Database()
    db.add_callmap({"print": print})

    result = True

    result = result and DefineStatement(db, "opisz", ["Panna Młoda"], [
        RunStatement(db, "lokacja_gracza", ["Izba"]),
        CallStatement(db, "print", ["Panna Młoda ma włosy i nogi"])
    ]).run()

    RunStatement(db, "opisz", ["Panna Młoda"]).run()

    AssertStatement(db, "lokacja_gracza", ["Izba"]).run()

    RunStatement(db, "opisz", ["Panna Młoda"]).run()

    captured = capsys.readouterr()
    assert captured.out == (
        "Panna Młoda ma włosy i nogi\n"
    ) and result


def test_conditionals(capsys):
    db = Database()
    db.add_callmap({"print": print})

    result = True

    result = result and DefineStatement(db, "opisz", ["Goście Weselni"], [
        IfStatement(db, "", [], [
            RunStatement(db, "lokacja_postaci", ["Wilkołak", "Izba"])
        ], [
            CallStatement(db, "print", ["Goście Weselni są aktualnie zjadani"])
        ], [
            CallStatement(db, "print", ["Goście Weselni się weselą, duh"])
        ])
    ]).run()

    RunStatement(db, "opisz", ["Goście Weselni"]).run()

    AssertStatement(db, "lokacja_postaci", ["Wilkołak", "Izba"]).run()

    RunStatement(db, "opisz", ["Goście Weselni"]).run()

    captured = capsys.readouterr()
    assert captured.out == (
        "Goście Weselni się weselą, duh\n"
        "Goście Weselni są aktualnie zjadani\n"
    ) and result


def test_operators(capsys):
    db = Database()
    db.add_callmap({"print": print})

    result = True

    result = result and DefineStatement(db, "opisz", ["Panna Młoda"], [
        IfStatement(db, "", [], [
            EitherStatement(db, "", [], [
                RunStatement(db, "lokacja_postaci", ["Wilkołak", "Izba"]),
                RunStatement(db, "lokacja_postaci", ["Wampir", "Izba"])
            ])
        ], [
            NotStatement(db, "martwa_postać", ["Panna Młoda"]),
            CallStatement(db, "print", ["Panna Młoda aktualnie jest zjadana"])
        ], [
            CallStatement(db, "print", ["Panna Młoda sobie siedzi"])
        ])
    ]).run()

    RunStatement(db, "opisz", ["Panna Młoda"]).run()

    AssertStatement(db, "lokacja_postaci", ["Wilkołak", "Izba"]).run()

    RunStatement(db, "opisz", ["Panna Młoda"]).run()

    RetractStatement(db, "lokacja_postaci", ["Wilkołak", "Izba"]).run()

    AssertStatement(db, "lokacja_postaci", ["Wampir", "Izba"]).run()

    RunStatement(db, "opisz", ["Panna Młoda"]).run()

    AssertStatement(db, "lokacja_postaci", ["Wilkołak", "Izba"]).run()

    RunStatement(db, "opisz", ["Panna Młoda"]).run()

    captured = capsys.readouterr()
    assert captured.out == (
        "Panna Młoda sobie siedzi\n"
        "Panna Młoda aktualnie jest zjadana\n"
        "Panna Młoda aktualnie jest zjadana\n"
        "Panna Młoda aktualnie jest zjadana\n"
    ) and result


def test_simple_communication(capsys):
    db = Database()
    db.add_callmap({
        "print": print,
        "rpg.boolean_test": (lambda *args: db.set_bool(True)),
        "is_true": (lambda *args: db.get_bool())
    })

    result = True

    result = result and not RunStatement(db, "martwa_postać", ["Pan Młody"]).run()

    result = result and DefineStatement(db, "zaatakuj", ["Pan Młody", "Strzelba"], [
        CallStatement(db, "rpg.boolean_test", ["Domokrążca", "Strzelectwo", "Strzelba"]),
        IfStatement(db, "", [], [
            CallStatement(db, "is_true", [])
        ], [
            AssertStatement(db, "martwa_postać", ["Pan Młody"])
        ], [
            RunStatement(db, "chybiony_strzał", [])
        ])
    ]).run()

    RunStatement(db, "zaatakuj", ["Pan Młody", "Strzelba"]).run()

    result = result and RunStatement(db, "martwa_postać", ["Pan Młody"]).run()
    
    assert result
