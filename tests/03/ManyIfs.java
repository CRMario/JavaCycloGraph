public class ManyIfs {
 
    public String grade(int score) {
        // unknown score value
        if (score >= 90) {
            return "A";
        } else if (score >= 80) {
            return "B";
        } else if (score >= 70) {
            return "C";
        } else {
            return "F";
        }
    }
 
    public int sign(int n) {
        // unknown n value
        if (n > 0) {
            return 1;
        } else if (n < 0) {
            return -1;
        } else {
            return 0;
        }
        return 5;
    }
}