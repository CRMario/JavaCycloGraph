class Calculator {
    int checkValue(int input) {
        int limit = 10;
        int result = 0;
        
        if (input < limit) {
            result = 1;
        } else {
            result = 2;
        }
        
        return result;
    }
}