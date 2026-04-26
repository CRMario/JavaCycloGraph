public class TryCatch {
 
    public int safeDivide(int a, int b) {
        int result = 0;
        try {
            result = a / b;
        } catch (Exception e) {
            result = -1;
        }
        return result;
    }
 
    public void withFinally(int x) {
        int a = 0;
        try {
            a = x + 1;
        } catch (Exception e) {
            a = -1;
        } finally {
            a = 0;
        }
    }
 
    public int multiCatch(int x) {
        int result = 0;
        try {
            result = x / 2;
        } catch (Exception e) {
            result = -1;
        } catch (Exception e) {
            result = -2;
        }
        return result;
    }
}
 