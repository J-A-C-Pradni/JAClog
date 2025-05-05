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

def test_cut_off(capsys):
    db = Database()
    db.add_callmap({"print": print})

    EitherStatement(db, "order", [], [
        CallStatement(db, "print", ["This should show up"]),
        RunStatement(db, "lokacja_postaci", ["Wilkołak", "Izba"]),
        CallStatement(db, "print", ["Whereas this should not"])
    ]).run()

    captured = capsys.readouterr()
    assert captured.out == (
        "This should show up\n"
    )

def test_vdefine(capsys):
    db = Database()
    db.add_callmap({"print": print})

    VDefineStatement(db, "opisz", [Var("Lokacja")], [
        CallStatement(db, "print", ["Jest to z pewnością lokacja"])
    ]).run()

    RunStatement(db, "opisz", ["Izba"]).run()

    captured = capsys.readouterr()
    assert captured.out == (
        "Jest to z pewnością lokacja\n"
    )

def test_vdefine_order(capsys):
    db = Database()
    db.add_callmap({"print": print})

    DefineStatement(db, "opisz", ["Izba"], [
        CallStatement(db, "print", ["Jest to izba!"])
    ]).run()
    
    VDefineStatement(db, "opisz", [Var("Lokacja")], [
        CallStatement(db, "print", ["Jest to z pewnością lokacja"])
    ]).run()

    RunStatement(db, "opisz", ["Izba"]).run()
    RunStatement(db, "opisz", ["Studnia"]).run()

    captured = capsys.readouterr()
    assert captured.out == (
        "Jest to izba!\n"
        "Jest to z pewnością lokacja\n"
    )

def test_multiple_vrules(capsys):
    db = Database()
    db.add_callmap({"print": print})

    VDefineStatement(db, "opisz", [Var("Lokacja")], [
        CallStatement(db, "print", ["Jest to z pewnością lokacja"])
    ]).run()

    VDefineStatement(db, "opisz", [Var("Miejsce")], [
        CallStatement(db, "print", ["Jest to z pewnością lokacja"])
    ]).run()

    print(db)

    captured = capsys.readouterr()
    assert captured.out == (
        "opisz(VAR Lokacja) + 1\n"
    )
