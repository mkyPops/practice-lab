// String search demo: KMP (failure-function based) and Rabin-Karp (rolling hash)
// pattern matching, both returning all starting indices of matches in text.

#include <iostream>
#include <string>
#include <vector>

// Build the KMP failure function (longest proper prefix that is also a suffix).
std::vector<int> buildFailureFunction(const std::string& pattern) {
    std::vector<int> fail(pattern.size(), 0);
    int k = 0;
    for (size_t i = 1; i < pattern.size(); ++i) {
        while (k > 0 && pattern[i] != pattern[k]) {
            k = fail[k - 1];
        }
        if (pattern[i] == pattern[k]) {
            ++k;
        }
        fail[i] = k;
    }
    return fail;
}

// KMP search: returns all indices in text where pattern occurs.
std::vector<int> kmpSearch(const std::string& text, const std::string& pattern) {
    std::vector<int> matches;
    if (pattern.empty()) return matches;

    std::vector<int> fail = buildFailureFunction(pattern);
    int k = 0;
    for (size_t i = 0; i < text.size(); ++i) {
        while (k > 0 && text[i] != pattern[k]) {
            k = fail[k - 1];
        }
        if (text[i] == pattern[k]) {
            ++k;
        }
        if (k == static_cast<int>(pattern.size())) {
            matches.push_back(static_cast<int>(i) - k + 1);
            k = fail[k - 1];
        }
    }
    return matches;
}

// Rabin-Karp search using a polynomial rolling hash with modular reduction.
std::vector<int> rabinKarpSearch(const std::string& text, const std::string& pattern) {
    std::vector<int> matches;
    size_t n = text.size(), m = pattern.size();
    if (m == 0 || m > n) return matches;

    const long long base = 256;
    const long long mod = 1'000'000'007LL;

    long long patternHash = 0, windowHash = 0, highOrder = 1;
    for (size_t i = 0; i < m; ++i) {
        patternHash = (patternHash * base + pattern[i]) % mod;
        windowHash = (windowHash * base + text[i]) % mod;
        if (i > 0) highOrder = (highOrder * base) % mod;
    }

    for (size_t i = 0; i + m <= n; ++i) {
        if (windowHash == patternHash && text.compare(i, m, pattern) == 0) {
            matches.push_back(static_cast<int>(i));
        }
        if (i + m < n) {
            windowHash = (windowHash - text[i] * highOrder % mod + mod) % mod;
            windowHash = (windowHash * base + text[i + m]) % mod;
        }
    }
    return matches;
}

static void printMatches(const std::string& label, const std::vector<int>& matches) {
    std::cout << label << ": ";
    for (int idx : matches) std::cout << idx << " ";
    std::cout << (matches.empty() ? "(none)" : "") << "\n";
}

int main() {
    std::string text = "ababcababcabc";
    std::string pattern = "abc";

    printMatches("KMP matches", kmpSearch(text, pattern));
    printMatches("Rabin-Karp matches", rabinKarpSearch(text, pattern));

    return 0;
}
