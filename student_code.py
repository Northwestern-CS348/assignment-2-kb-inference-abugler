import read, copy
from util import *
from logical_classes import *

verbose = 0

class KnowledgeBase(object):
    def __init__(self, facts=[], rules=[]):
        self.facts = facts
        self.rules = rules
        self.ie = InferenceEngine()

    def __repr__(self):
        return 'KnowledgeBase({!r}, {!r})'.format(self.facts, self.rules)

    def __str__(self):
        string = "Knowledge Base: \n"
        string += "\n".join((str(fact) for fact in self.facts)) + "\n"
        string += "\n".join((str(rule) for rule in self.rules))
        return string

    def _get_fact(self, fact):
        """INTERNAL USE ONLY
        Get the fact in the KB that is the same as the fact argument

        Args:
            fact (Fact): Fact we're searching for

        Returns:
            Fact: matching fact
        """
        for kbfact in self.facts:
            if fact == kbfact:
                return kbfact

    def _get_rule(self, rule):
        """INTERNAL USE ONLY
        Get the rule in the KB that is the same as the rule argument

        Args:
            rule (Rule): Rule we're searching for

        Returns:
            Rule: matching rule
        """
        for kbrule in self.rules:
            if rule == kbrule:
                return kbrule

    def kb_add(self, fact_rule):
        """Add a fact or rule to the KB
        Args:
            fact_rule (Fact|Rule) - the fact or rule to be added
        Returns:
            None
        """
        printv("Adding {!r}", 1, verbose, [fact_rule])
        if isinstance(fact_rule, Fact):
            if fact_rule not in self.facts:
                self.facts.append(fact_rule)
                for rule in self.rules:
                    self.ie.fc_infer(fact_rule, rule, self)
            else:
                if fact_rule.supported_by:
                    ind = self.facts.index(fact_rule)
                    for f in fact_rule.supported_by:
                        self.facts[ind].supported_by.append(f)
                else:
                    ind = self.facts.index(fact_rule)
                    self.facts[ind].asserted = True
        elif isinstance(fact_rule, Rule):
            if fact_rule not in self.rules:
                self.rules.append(fact_rule)
                for fact in self.facts:
                    self.ie.fc_infer(fact, fact_rule, self)
            else:
                if fact_rule.supported_by:
                    ind = self.rules.index(fact_rule)
                    for f in fact_rule.supported_by:
                        self.rules[ind].supported_by.append(f)
                else:
                    ind = self.rules.index(fact_rule)
                    self.rules[ind].asserted = True

    def kb_assert(self, fact_rule):
        """Assert a fact or rule into the KB

        Args:
            fact_rule (Fact or Rule): Fact or Rule we're asserting
        """
        printv("Asserting {!r}", 0, verbose, [fact_rule])
        self.kb_add(fact_rule)

    def kb_ask(self, fact):
        """Ask if a fact is in the KB

        Args:
            fact (Fact) - Statement to be asked (will be converted into a Fact)

        Returns:
            listof Bindings|False - list of Bindings if result found, False otherwise
        """
        print("Asking {!r}".format(fact))
        if factq(fact):
            f = Fact(fact.statement)
            bindings_lst = ListOfBindings()
            # ask matched facts
            for fact in self.facts:
                binding = match(f.statement, fact.statement)
                if binding:
                    bindings_lst.add_bindings(binding, [fact])

            return bindings_lst if bindings_lst.list_of_bindings else []

        else:
            print("Invalid ask:", fact.statement)
            return []

    def kb_retract(self, fact_or_rule):
        """Retract a fact from the KB

        Args:
            fact (Fact) - Fact to be retracted

        Returns:
            None
        """
        printv("Retracting {!r}", 0, verbose, [fact_or_rule])
        ####################################################
        # Student code goes here

        if isinstance(fact_or_rule, Fact):
            for f in self.facts:
                if f == fact_or_rule:
                    fact_or_rule = f;
                    break;
            fact_or_rule.asserted = False;
            if not fact_or_rule.supported_by:
                for fact in fact_or_rule.supports_facts:
                    fact.supported_by.remove(fact_or_rule);
                    for support in fact.supported_by:
                        if isinstance(support, Rule) and match(support.lhs[0], fact_or_rule.statement):
                            fact.supported_by.remove(support)
                    if not fact.supported_by and not fact.asserted:
                        self.kb_retract(fact)
                for rule in fact_or_rule.supports_rules:
                    rule.supported_by.remove(fact_or_rule)
                    for support in rule.supported_by:
                        if isinstance(support, Rule) and match(support.lhs[0], fact_or_rule.statement):
                            rule.supported_by.remove(support)
                    if not rule.supported_by and not rule.asserted:
                        self.rules.remove(rule)
                self.facts.remove(fact_or_rule)
        """
        for fact in fact_or_rule.supports_facts:
            fact.supported_by.remove(fact_or_rule)
            if not fact.supported_by:
                self.kb_retract(fact)
        for rule in fact_or_rule.supports_facts:
            fact.supported_by.remove(fact_or_rule)
            if not fact.supported_by:
                self.kb_retract(rule)
        if isinstance(fact_or_rule, Fact):
            self.facts.remove(fact_or_rule)
        if isinstance(fact_or_rule, Rule):
            self.rules.remove(fact_or_rule)
        """




class InferenceEngine(object):
    def fc_infer(self, fact, rule, kb):
        """Forward-chaining to infer new facts and rules

        Args:
            fact (Fact) - A fact from the KnowledgeBase
            rule (Rule) - A rule from the KnowledgeBase
            kb (KnowledgeBase) - A KnowledgeBase

        Returns:
            Nothing
        """
        printv('Attempting to infer from {!r} and {!r} => {!r}', 1, verbose,
            [fact.statement, rule.lhs, rule.rhs])
        ####################################################
        # Student code goes here
        bindings = match(fact.statement, rule.lhs[0]);
        if bindings:
            """
            if fact == kb.facts[len(kb.facts)-1]:
                if len(rule.lhs) <= 1:
                    newFact = Fact(instantiate(rule.rhs, bindings), [])
                    newFact.supported_by.append(fact)
                    newFact.supported_by.append(rule)
                    fact.supports_facts.append(newFact)
                    rule.supports_facts.append(newFact)
                    if newFact not in kb.facts:
                        kb.facts.append(newFact)
                    else:
                        newRule = Rule()
                        i = 0
                        for statement in rule.lhs:
                            if i:
                                newRule.lhs.append(instantiate(statement, bindings))
                            i += 1
                        newRule.rhs = instantiate(rule.rhs, bindings)
                        newRule.supported_by.append(fact)
                        newRule.supported_by.append(rule)
                        fact.supports_rules.append(newRule)
                        rule.supports_rules.append(newRule)
                        if newRule not in kb.rules:
                            kb.rules.append(newRule)
            elif rule == kb.rules[len(kb.rules)-1]:
                """

            if len(rule.lhs) == 1:
                newFact = Fact(instantiate(rule.rhs, bindings), [])
                if newFact not in kb.facts:
                    newFact.supported_by.append(fact)
                    newFact.supported_by.append(rule)
                    newFact.asserted = False
                    fact.supports_facts.append(newFact)
                    rule.supports_facts.append(newFact)
                    printv('{!r}', 1, verbose, [newFact.statement])
                    kb.facts.append(newFact)
                    for r in kb.rules:
                        self.fc_infer(newFact, r, kb)
            else:
                newRule = Rule('rule', [])
                i = 0
                for statement in rule.lhs:
                    if i == 1:
                        newRule.lhs[0] = instantiate(statement, bindings)
                    elif i:
                        newRule.lhs.append(instantiate(statement, bindings))
                    i += 1
                newRule.rhs = instantiate(rule.rhs, bindings)
                if newRule not in kb.rules:
                    newRule.supported_by.append(fact)
                    newRule.supported_by.append(rule)
                    newRule.asserted = False
                    fact.supports_rules.append(newRule)
                    rule.supports_rules.append(newRule)
                    printv('{!r}=>{!r}', 1, verbose, [newRule.lhs, newRule.rhs])
                    kb.rules.append(newRule)
                    for f in kb.facts:
                        self.fc_infer(f, newRule, kb)






