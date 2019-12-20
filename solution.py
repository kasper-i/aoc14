#!/usr/bin/env python3
import sys


class QuantifiedChemical(object):
    def __init__(self, name, quantity):
        self.name = name
        self.quantity = quantity

    def __str__(self):
        return "(%d, %s)" % (self.quantity, self.name)


class Formula(object):
    def __init__(self, chemicals, product):
        self.chemicals = chemicals
        self.product = product

    def __str__(self):
        return "Formula(chemicals=[%s], product=%s)" % (", ".join(["%s" % (c,) for c in self.chemicals]), self.product)


class RecyclingBin(object):
    def __init__(self):
        self.quantities = dict()

    def put(self, name, quantity):
        if name not in self.quantities:
            self.quantities[name] = 0

        self.quantities[name] += quantity

    def recycle(self, name, required_quantity):
        if name in self.quantities:
            recycled = min(self.quantities[name], required_quantity)
            self.quantities[name] -= recycled
            return recycled
        else:
            return 0

    def clone(self):
        cloned_quantities = dict()

        for k, v in self.quantities.items():
            cloned_quantities[k] = v

        clone = RecyclingBin()
        clone.quantities = cloned_quantities
        return clone


class OreCalculator(object):
    def __init__(self, formulas):
        self.formulas_by_product = dict()

        for r in formulas:
            self.formulas_by_product[r.product.name] = r

        self.recycling_bin = RecyclingBin()

    def calculate(self, multiplier):
        fuel_formula = self.formulas_by_product['FUEL']

        required_chemicals = []
        for qc in fuel_formula.chemicals:
            required_chemicals.append(QuantifiedChemical(qc.name, multiplier * qc.quantity))

        return self.__calc_ore(required_chemicals)

    def __calc_ore(self, chemicals):
        if len(chemicals) == 1:
            chemical = chemicals[0]
            quantity, name = chemical.quantity, chemical.name

            quantity -= self.recycling_bin.recycle(name, quantity)

            if name == "ORE":
                return quantity
            else:
                formula = self.formulas_by_product[name]

                multiplier = quantity // formula.product.quantity
                if quantity % formula.product.quantity > 0:
                    multiplier += 1

                required_chemicals = []
                for qc in formula.chemicals:
                    required_chemicals.append(QuantifiedChemical(qc.name, multiplier * qc.quantity))

                waste = multiplier * formula.product.quantity - quantity
                self.recycling_bin.put(formula.product.name, waste)
                
                return self.__calc_ore(required_chemicals)
        else:
            total_ore = 0
            for c in chemicals:
                total_ore += self.__calc_ore([c])
            
            return total_ore


def main():
    input_ = sys.argv[1]

    formulas = []
    with open(input_, "r") as f:
        lines = f.readlines()
        for formula in parse(lines):
            print(formula)
            formulas.append(formula)

    calculator = OreCalculator(formulas)
    ore = calculator.calculate(1)
    print("Minimum ORE required: %d" % (ore,))

    calculator = OreCalculator(formulas)
    ore_inventory = 1000000000000
    fuel_produced = 0

    multiplier = ore_inventory

    while ore_inventory > 0:
        if multiplier > 1:
            previous_recycling_bin = calculator.recycling_bin.clone()

        ore_consumed = calculator.calculate(multiplier)

        if (ore_inventory - ore_consumed) < 0 and multiplier > 1:
            multiplier //= 10
            calculator.recycling_bin = previous_recycling_bin
            continue

        ore_inventory -= ore_consumed

        if ore_inventory >= 0:
            fuel_produced += multiplier

    print("1 trillion ORE would produce %d FUEL" % (fuel_produced,))

def parse(lines):
    for line in lines:
        chemicals, _, product = line.partition("=>")
        product = parse_quantity_and_chemical(product)
        chemicals = [parse_quantity_and_chemical(x) for x in chemicals.split(",")]
        
        yield Formula(chemicals, product)


def parse_quantity_and_chemical(input_):
    quantity, _, name = input_.strip().partition(" ")
    return QuantifiedChemical(name, int(quantity))


if __name__ == "__main__":
    main()
