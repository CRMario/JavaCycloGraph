public class Loops {
 
    public int countDown(int n) {
        int count = 0;
        do {
            count = count + 1;
            n--;
        } while (n > 0);
        return count;
    }
 
    public int nestedFor(int n) {
        int sum = 0;
        for (int i = 0; i < n; i++) {
            for (int j = 0; j < n; j++) {
                sum = sum + 1;
            }
        }
        return sum;
    }
 
    public int forInsideIf(int n) {
        int result = 0;
        if (true) {
            for (int i = 0; i < n; i++) {
                result = result + i;
            }
        } else {
            result = -1;
        }
        return result;
    }
}
 