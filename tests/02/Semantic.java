public class SemanticErrors {
 
    // undeclared variable
    public int useUndeclared() {
        int x = 5;
        int y = z + 1;
        return y;
    }

    // assign incorrect type
    private void hello() {
        int x;
        x = "Hello";
        return;
    }

    // arithmetic
    public void arithmetic() {
        boolean x = true;
        boolean y = false;
        return x + y;
    }

    // logical
    private void logical() {
        int x = 5;
        int y = 6;
        return (x && y);
    }

    // conditions
    public int noConditionIf() {
        int x = 5;
        if (x) {
            x = 6;
        }
        return x;
    }
 
    // correct method — should be all green
    public int correct() {
        int a = 1;
        int b = 2;
        int c = a + b;
        return c;
    }
}