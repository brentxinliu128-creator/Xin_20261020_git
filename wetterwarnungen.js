class
WetterWarnungen {
    constructor() {
        this.abonnements = [];
    }

    abonnieren(email, regionen) {
        this.abonnements.push({"brentxinliu128@gmail.com", "DE-BY"});
    }

    getAbonnements() {
        return this.abonnements;
    }
}