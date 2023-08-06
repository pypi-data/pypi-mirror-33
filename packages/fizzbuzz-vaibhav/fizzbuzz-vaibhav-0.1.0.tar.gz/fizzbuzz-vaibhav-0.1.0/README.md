# Knoxpy Fizzbuzz

This is a package that was created for the knoxpy meetup on July
5th 2018. It follows my **OPINIONATED** [guide on Python
packaging](https://costrouc-python-package-template.readthedocs.io/en/latest/)
that I update as I learn what I consider to be a best new way to do
packaging in Python. The non python dependencies that this tutorial
assumes is the user has a gitlab repository. It can easily be used
with Github if hooked up with the [Gitlab
Runners](https://docs.gitlab.com/ee/ci/ci_cd_for_external_repos/github_integration.html).

I conducted a survey on the knoxdevs python slack channel asking what
are the most important things that others would like covered. By the
end of this tutorial you should have a python package that is...

1. documented (available on readthedocs updated on each commit)
2. tested (automated testing on each commit)
3. deployed to PyPi (automated deployment on each passing tagged commit)
4. deployed to Conda (automated deployement on each passing tagged commit)

This repository takes advantage of git tags to allow people to jump to
each step if they get lost. To view all the steps `git tag`. To go to
a specific tag use the `checkout` command. For example to start out
you will run `git check step-1`.

 - step-1: simplest python "package"
 - step-2: improved python "package" (show zip trick)
 - step-3: deploying to pypi ([twine](https://github.com/pypa/twine))
 - step-4: automating pypi deployment [gitlab CI](https://about.gitlab.com/features/gitlab-ci-cd/)
 - step-5: deploying to conda ([conda-build](https://conda.io/docs/user-guide/tasks/build-packages/index.html))
 - step-6: automating conda deployment [gitlab CI](https://about.gitlab.com/features/gitlab-ci-cd/)
 - step-7: adding testing [pytest](https://docs.pytest.org/en/latest/)
 - step-8: automating testing [gitlab CI](https://about.gitlab.com/features/gitlab-ci-cd/)
 - step-9: adding documentation [sphinx](http://www.sphinx-doc.org/en/master/)
 - step-10: automating documentation ([readthedocs](https://readthedocs.org/) + [gitlab pages](https://about.gitlab.com/features/pages/))

