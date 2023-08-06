"""a temporary python script for small tests"""
from flloat.base.Symbol import Symbol
from flloat.parser.ldlf import LDLfParser
from flloat.parser.ltlf import LTLfParser
from flloat.semantics.ldlf import FiniteTrace


def k(n):
    from flloat.base.Symbol import Symbol
    from flloat.parser.ldlf import LDLfParser
    parser = LDLfParser()
    cc = ["c%d" % d for d in range(n)]
    labels = [Symbol(d) for d in cc]
    f = "<%s>tt" % ";".join(cc)
    print(f)

    f = parser(f)
    nfa = f.to_automaton(labels)
    nfa.to_dot("temp_nfa.NFA")
    print("nfa")
    dfa = nfa.determinize()
    dfa.to_dot("temp_det.DFA")
    print("dfa")
    dfa = dfa.minimize().trim()
    dfa.to_dot("temp_min.DFA")
    print("dfatrim")

def breakout_formula():
    p = LDLfParser()
    f = p("<(!l0 & !l1 & !l2)*;(l0 & !l1 & !l2);(l0 & !l1 & !l2)*;(l0 & l1 & !l2); (l0 & l1 & !l2)*; l0 & l1 & l2>tt")
    f.to_automaton(determinize=True).to_dot("temp")

def reward_shaping_example_formula():
    p = LDLfParser()
    a, b, c = [Symbol(c) for c in "ABC"]
    f = p("<A*; B>tt")
    f.to_automaton({a, b, c}, determinize=True).complete().to_dot("temp.DFA")
    f.to_automaton({a, b, c}).to_dot("temp.NFA")
    k = f.to_automaton({a, b, c}, on_the_fly=True)

    t_false = FiniteTrace.fromStringSets([
        {"A"},
        {"A"},
        {"C"},
        {"B"}
    ])

    t_true = FiniteTrace.fromStringSets([
        {"A"},
        {"A"},
        {"B"},
        {"B"}
    ])

    # k.word_acceptance(t_false.trace)
    # k.word_acceptance(t_true.trace)

    print(k.cur_state)
    for s in t_true.trace:
        k.make_transition(s)
        print(k.cur_state)

def sapientino_test():
    p = LTLfParser()
    #  | cellC0_1 | cellC0_2
    f = "(!b U (cellC0_0 & b)) & G (cellC0_0 & b -> X(G b -> !cellC0_0))"
    # "G (cellC0_1 & b -> X(G b -> !cellC0_1))"

    # (!b U (cellC0_0 & b)) &
    f = "G (cellC0_0 & b -> X(G (b -> !cellC0_0)) )"
    # f = "G (A -> X(G (B -> C)) )"
    f = "G ( A -> X(G(B)) )"
    # f = "G (A -> X(B) )"
    # f = "X(F A)"
    f = '''(!b U ( (A | B | C) & b))
                & (G (A & b -> X(G (b -> !A) ) ) )
                & (G (B & b -> X(G (b -> !B) ) ) )
                & (G (C & b -> X(G (b -> !C) ) ) )
                & (
                      (G (A & b -> X( !b U ((B | C) & b) ) ) )
                    | (G (B & b -> X( !b U ((A | C) & b) ) ) )
                    | (G (C & b -> X( !b U ((A | B) & b) ) ) )
                )'''

    # f = '''(!b U ( A & b & !END))
    #                 & (G (A & b -> X(G (b -> !A) ) ) )
    #                 & (G (A & b -> X( !b U END & b ) ) )'''

    # f = '''(!b U ( (A | B) & b))
    #                 & (G (A & b -> X(G (b -> !A) ) ) )
    #                 & (G (B & b -> X(G (b -> !B) ) ) )
    #                 & (
    #                       (G (A & b -> X( !b U ( B & b) ) ) )
    #                     | (G (B & b -> X( !b U ( A & b) ) ) )
    #                 )'''

    print(f)
    # f = '''(!b U ( (A | B) & b ))
    #             & (G (A & b -> X( G (b -> !A) ) ) )
    #             & (G (B & b -> X( G (b -> !B) ) ) )'''

    # f = '''(!b U A & b | B & b)
    #             & G (b & (A|B))
    #             & (F (A & b)) & (F (B & b))
    #             & (G (A & b -> X( G (b -> !A) ) ) )
    #             & (G (B & b -> X( G (b -> !B) ) ) )'''

    # & (G(A & b -> X( !b U B & b) ) )
    # & (G(B & b -> X( !b U A & b) ) )


    # print(p(f))
    # print(p(f).to_automaton().to_dot("nfa"))

    p(f).to_automaton(determinize=True, minimize=True).map_to_int().to_dot("TEMP.ltlf")

    # nfa = p(f).to_automaton(determinize=False, minimize=False)
    # nfa.map_to_int().to_dot("OLD_TEMP_NFA.ltlf.nfa")
    # dfa = nfa.determinize().trim().minimize().trim()
    # dfa.map_to_int().to_dot("OLD_TEMP_MIN_TRIM_DFA.ltlf.dfa")

    # dfa = p(f).to_automaton(minimize=False)
    # dfa = dfa.map_states_and_action(states_map={v: k for k, v in enumerate(dfa.states)})
    # dfa.to_dot("TEMP.ltlf")

    # p = LDLfParser()
    # p("[true](<A>tt)").to_automaton(determinize=True).to_dot("temptemp.ldlf")

def ldlf_ltlf():
    d = LDLfParser()
    # d("<(!b)*; A & b & !(B | C | D | E | F); "
    #    "(!b)*; B & b & !(A | C | D | E | F); "
    #    "(!b)*; C & b & !(B | A | D | E | F); "+
    #    "(!b)*; D & b & !(B | C | A | E | F); "
    #    "(!b)*; E & b & !(B | C | D | A | F); "
    #    "(!b)*; F & b & !(B | C | D | E | A)>tt").to_automaton(determinize=True).to_dot("temptemp.ldlf")

    # d("<A;B;C;D;E;F;G;H;I;L;M;N;O;P>tt").to_automaton(determinize=True, minimize=False)
        # .to_dot("temptemp.ldlf")

    d("<(!bip)*;red & bip;(!bip)*;green & bip;(!bip)*;blue & bip;(!bip)*;pink & bip;(!bip)*;brown & bip;(!bip)*;gray & bip;(!bip)*;purple & bip;(!bip)*;no_color & bip>tt") \
        .to_automaton(determinize=True, minimize=True).to_dot("temptemp.ldlf")

    # d("[((<true>tt)?;true)*]([true]ff | <A>tt)").to_automaton(determinize=False, minimize=False).to_dot("temptemp.ldlf.1")
    # d("[((<true>tt)?;true)*]([true]ff | <A>tt)").to_automaton(determinize=True, minimize=False).to_dot("temptemp.ldlf.2")
    # d("[((<true>tt)?;true)*]([true]ff | <A>tt)").to_automaton(determinize=True, minimize=True).to_dot("temptemp.ldlf.3")
    # d("[true*]([true]ff | <A>tt)").to_automaton(determinize=True, minimize=True).to_dot("temptemp.ldlf")

    # d("<((<true>tt)?;true)*>(<true>tt & <A>tt)").to_automaton(determinize=True).to_dot("temptemp.ldlf")
    # d("<true*>(<true>tt & <A>tt)").to_automaton(determinize=True).to_dot("temptemp.ldlf")

    # ltlfp = LTLfParser()
    # f = "G ( A -> X(G(B)) )"
    # print(ltlfp(f).to_LDLf().to_nnf())
    # ltlfp(f).to_LDLf().to_automaton(determinize=True, minimize=True).to_dot("temptemp.ltlf")
    # ltlfp("WX AAAA").to_LDLf().to_automaton(determinize=True, minimize=True).to_dot("temptemp.ltlf")


def sapientino_ldlf():
    # f = "<(!bip)*;red & bip;(!bip)*;green & bip;(!bip)*;blue & bip;(!bip)*;pink & bip;(!bip)*;brown & bip;(!bip)*;gray & bip;(!bip)*;purple & bip>tt"
    # d = LDLfParser()
    # parsed = d(f)
    # parsed.to_automaton(determinize=True, minimize=True).to_dot("sapientino_ldlf_1")

    # f = "<true*;red & bip;true*;green & bip;true*;blue & bip;true*;pink & bip;true*;brown & bip;true*;gray & bip;true*;purple & bip>tt & " \
    #     " [((<true>tt)?;true)*](<bip -> (red | green | blue | pink | brown | gray | purple)>tt  | [true]ff)"
    f = " [true*](<bip -> (A | C)>tt  | [true]ff)"
    d = LDLfParser()
    parsed = d(f)
    parsed.to_automaton(determinize=True, minimize=True).to_dot("sapientino_ldlf_2")


def minecraft_ldlf():
    # f = "<(!get & !use)*;get & wood; (!get & !use)*;use & workbench; (!get & !use)*;get & iron; (!get & !use)*; use & toolshed>tt"
    f = "<true*><true;A;B>tt"
    # f = "[true*](<!get & !use>tt | [true]ff)"
    # f = "[true*](<(get | use) -> (wood | grass | iron | gold | gem | toolshed | workbench | factory) >tt | [true]ff)"
    f = "<(!l0 & !l1 & !l2)*;(l0 & !l1 & !l2);(l0 & !l1 & !l2)*;(l0 & l1 & !l2); (l0 & l1 & !l2)*; l0 & l1 & l2>tt"
    d = LDLfParser()

    # f = "<true*>(<true*;A;true*;B;true*;C>tt)"

    # f = "F(A & F(B & F(C)))"
    # d = LTLfParser()


    parsed = d(f)
    parsed.to_automaton(determinize=True, minimize=True)._numbering_states().to_dot("breakout")



if __name__ == '__main__':
    pass
    # k(4)
    # p = LTLfParser()
    # p("A U B").to_automaton(determinize=True).to_dot("temptemp.ltlf")
    #

    # sapientino_test()
    # ldlf_ltlf()
    # sapientino_ldlf()
    minecraft_ldlf()
