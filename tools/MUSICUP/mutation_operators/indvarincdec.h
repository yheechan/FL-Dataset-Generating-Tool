#ifndef MUSIC_IndVarIncDec_H_
#define MUSIC_IndVarIncDec_H_ 

#include "expr_mutant_operator.h"

class IndVarIncDec : public ExprMutantOperator
{
public:
  IndVarIncDec(const std::string name = "IndVarIncDec")
    : ExprMutantOperator(name)
  {}

  virtual bool ValidateDomain(const std::set<std::string> &domain);
  virtual bool ValidateRange(const std::set<std::string> &range);

  // Return True if the mutant operator can mutate this expression
  virtual bool IsMutationTarget(clang::Expr *e, MusicContext *context);

  virtual void Mutate(clang::Expr *e, MusicContext *context);

private:
  bool IsIndVar(clang::Expr *e,MusicContext *context);
};

#endif  // MUSIC_IndVarIncDec_H_