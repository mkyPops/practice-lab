// kmp_rabinkarp.cpp
// Demonstrates two classic substring search algorithms:
//   1. Knuth-Morris-Pratt (KMP) using a failure function (prefix table).
//   2. Rabin-Karp using a polynomial rolling hash.
// Both return all starting indices where the pattern occurs in the text.

#include <iostream>
#include <string>
#include <vector>

// Build KMP failure function: lps[i] = length of longest proper prefix
// of pattern[0..i] that is also a suffix.
std::vector<int> buildFailureFunction(const std::string& pattern) {
    std::vector<int> lps(pattern.size(), 0);
    int len = 0;
    for (size_t i = 1; i < pattern.size(); ) {
        if (pattern[i] == pattern[len]) {
            lps[i++] = ++len;
        } else if (len != 0) {
            len = lps[len - 1];
        } else {
            lps[i++] = 0;
        }
    }
    return lps;
}

// KMP search: returns all match start positions.
std::vector<int> kmpSearch(const std::string& text, const std::string& pattern) {
    std::vector<int> matches;
    if (pattern.empty() || pattern.size() > text.size()) return matches;

    std::vector<int> lps = buildFailureFunction(pattern);
    size_t i = 0, j = 0; // i -> text index, j -> pattern index
    while (i < text.size()) {
        if (text[i] == pattern[j]) {
            ++i; ++j;
            if (j == pattern.size()) {
                matches.push_back(static_cast<int>(i - j));
                j = lps[j - 1]; // continue searching for overlapping matches
            }
        } else if (j != 0) {
            j = lps[j - 1];
        } else {
            ++i;
        }
    }
    return matches;
}

// Rabin-Karp search using a rolling hash with a large prime modulus.
std::vector<int> rabinKarpSearch(const std::string& text, const std::string& pattern) {
    std::vector<int> matches;
    size_t n = text.size(), m = pattern.size();
    if (m == 0 || m > n) return matches;

    const long long BASE = 256;
    const long long MOD = 1000000007LL;

    long long highOrder = 1; // BASE^(m-1) % MOD, used to drop leading char
    for (size_t i = 0; i + 1 < m; ++i) highOrder = (highOrder * BASE) % MOD;

    long long patternHash = 0, windowHash = 0;
    for (size_t i = 0; i < m; ++i) {
        patternHash = (patternHash * BASE + pattern[i]) % MOD;
        windowHash = (windowHash * BASE + text[i]) % MOD;
    }

    for (size_t i = 0; i + m <= n; ++i) {
        if (windowHash == patternHash) {
            // Verify to guard against hash collisions.
            if (text.compare(i, m, pattern) == 0) {
                matches.push_back(static_cast<int>(i));
            }
        }
        if (i + m < n) {
            windowHash = (windowHash - text[i] * highOrder % MOD + MOD) % MOD;
            windowHash = (windowHash * BASE + text[i + m]) % MOD;
        }
    }
    return matches;
}

static void printMatches(const std::string& label, const std::vector<int>& matches) {
    std::cout << label << ": ";
    for (int idx : matches) std::cout << idx << " ";
    std::cout << "\n";
}

int main() {
    std::string text = "abxabcabcabyabcabcaby";
    std::string pattern = "abcaby";

    printMatches("KMP matches", kmpSearch(text, pattern));
    printMatches("Rabin-Karp matches", rabinKarpSearch(text, pattern));

    return 0;
}
